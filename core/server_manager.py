from datetime import datetime

from pathlib import Path

from .compose_manager import ComposeManager
from .docker_manager import DockerManager
from .data_manager import DataManager
from .backup_manager import BackupManager
from .server_registry import ServerRegistry

class ServerManager:
    def __init__(self,
        compose_manager: ComposeManager,
        docker_manager: DockerManager,
        data_manager: DataManager, 
        server_registry: ServerRegistry,
        backup_manager: BackupManager,
        compose_directory: Path,
        servers_directory: Path,
        backups_directory: Path
    ):
        self.compose_manager = compose_manager
        self.docker_manager = docker_manager
        self.data_manager = data_manager
        self.server_registry = server_registry
        self.backup_manager = backup_manager

        self.compose_directory = Path(compose_directory)
        self.servers_directory = Path(servers_directory)
        self.backups_directory = Path(backups_directory)

    
    async def nonexistence_check(self, server_name: str):
        server_name_list = [server.name for server in self.server_registry.get_servers()]
        if server_name in server_name_list:
            raise ValueError(f"{server_name} already exists.")

    async def existence_check(self, server_name: str):
        server_name_list = [server.name for server in self.server_registry.get_servers()]
        if server_name not in server_name_list:
            raise ValueError(f"{server_name} doesn't exist.")

    async def container_check(self, server_name: str):
        if not await self.docker_manager.container_exists(server_name):
            raise ValueError(f"{server_name} container could not be found.")

    async def offline_check(self, server_name: str):
        if await self.docker_manager.is_online(server_name):
            raise ValueError(f"{server_name} must be offline.")

    async def online_check(self, server_name: str):
        if not await self.docker_manager.is_online(server_name):
            raise ValueError(f"{server_name} must be online.")

    async def create_server(self, context: dict, model_path: str):
        await self.nonexistence_check(context["server_name"])

        try:
            self.compose_manager.render(
                template_path=str(model_path),
                output_path=Path(context["compose_file"]),
                context=context
            )
            await self.docker_manager.compose_up(context["compose_file"])

        except Exception as e:
            if Path(context["compose_file"]).exists():
                try:
                    self.docker_manager.compose_down(context["compose_file"])
                except Exception:
                    pass

            self.data_manager.delete_directory(Path(context["compose_directory_path"]))
            self.data_manager.delete_directory(Path(context["server_directory_path"]))

            raise ValueError("Server could not be created.") from e

    async def delete_server(self, context: dict):
        await self.existence_check(context["server_name"])
        await self.container_check(context["server_name"])
        await self.offline_check(context["server_name"])

        try:
            await self.docker_manager.compose_down(Path(context["compose_file"]))
            await self.data_manager.delete_directory(Path(context["compose_directory_path"]))
            await self.data_manager.delete_directory(Path(context["server_directory_path"]))
        except Exception as e:
            raise ValueError("Server could not be deleted.") from e

    async def edit_server(self, context: dict, model_path: str):
        await self.existence_check(context["server_name"])
        await self.container_check(context["server_name"])
        await self.offline_check(context["server_name"])

        try:
            self.compose_manager.edit(
                template_path=str(model_path),
                existing_file=Path(context["compose_file"]),
                new_context=context
            )
            await self.docker_manager.create(context["compose_file"])
        except Exception as e:
            raise ValueError("Server could not be edited.") from e

    async def reset_server(self, context: dict):
        await self.existence_check(context["server_name"])
        await self.container_check(context["server_name"])
        await self.offline_check(context["server_name"])

        try:
            for directory_path in context["server_data_directory_paths"]:
                await self.data_manager.clear_directory(str(directory_path))
        except Exception as e:
            raise ValueError("Server could not be reset") from e

    async def backup_server(self, context: dict):
        await self.existence_check(context["server_name"])
        await self.container_check(context["server_name"])
        await self.offline_check(context["server_name"])

        context["backup_name"] = datetime.now().strftime("Backup_%Y-%m-%d-%H-%M")
        
        try:
            await self.backup_manager.backup_server(
                active_directory_path=Path(context["active_directory_path"]),
                active_data=context["active_data"],
                backup_directory_path=Path(context["backup_directory_path"]),
                backup_name=context["backup_name"]
            )
        except Exception as e:
            raise ValueError("Server state could not be saved.") from e

    async def delete_backup(self, context: dict):
        try:
            await self.backup_manager.delete_backup(
                backup_directory_path=Path(context["backup_directory_path"]),
                backup_name=context["backup_name"]
            )
        except Exception as e:
            raise ValueError("Backup could not be deleted.") from e

    async def restore_server(self, context: dict):
        await self.existence_check(context["server_name"])
        await self.container_check(context["server_name"])
        await self.offline_check(context["server_name"])

        if context["backup_name"] is None:
            available_backups = self.backup_manager.get_backups(Path(context["backup_directory_path"]))
            if not available_backups:
                raise ValueError("No backups available for this server.")
            context["backup_name"] = max(available_backups)

        try:
            await self.backup_manager.restore_server(
                active_directory_path=Path(context["active_directory_path"]),
                backup_directory_path=Path(context["backup_directory_path"]),
                backup_name=context["backup_name"]
            )
        except Exception as e:
            raise ValueError("Server backup could not be restored.") from e

    async def start_server(self, server_name: str):
        await self.existence_check(server_name)
        await self.container_check(server_name)
        await self.offline_check(server_name)

        await self.docker_manager.start(server_name)

    async def stop_server(self, server_name: str):
        await self.existence_check(server_name)
        await self.container_check(server_name)
        await self.online_check(server_name)

        await self.docker_manager.stop(server_name)

    async def restart_server(self, server_name: str):
        await self.existence_check(server_name)
        await self.container_check(server_name)

        await self.docker_manager.restart(server_name)

    async def status_server(self, server_name: str) -> dict:
        await self.existence_check(server_name)
        await self.container_check(server_name)

        return await self.docker_manager.status(server_name)

    async def list_servers(self) -> list:
        servers = [(server.name, server.game) for server in self.server_registry.get_servers()]
        servers.sort(key=lambda server: (server[1].lower(), server[0].lower()))
        return servers

    async def get_game(self, server_name: str) -> str:       
        await self.existence_check(server_name) 

        servers = {
            server.name: server.game
            for server in self.server_registry.get_servers()
        }

        return servers[server_name]

    async def execute_command(self, server_name: str, command: list[str]):
        await self.existence_check(server_name)
        await self.container_check(server_name)
        await self.online_check(server_name)

        try:
            await self.docker_manager.execute_command(server_name, command)
        except Exception as e:
            raise ValueError("Command could not be executed") from e
