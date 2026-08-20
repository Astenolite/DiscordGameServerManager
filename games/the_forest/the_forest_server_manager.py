from pathlib import Path

from games.abstract.game_server_manager import GameServerManager
from core.server_manager import ServerManager

from .config.the_forest_config import TheForestConfig
from .config.the_forest_server_create_config import TheForestServerCreateConfig
from .config.the_forest_server_edit_config import TheForestServerEditConfig 

class TheForestServerManager(GameServerManager):

    config = TheForestConfig
    server_create_config = TheForestServerCreateConfig
    server_edit_config = TheForestServerEditConfig

    def __init__(
        self, 
        server_manager: ServerManager,
    ):
        self.server_manager = server_manager

        self.the_forest_compose_directory = (server_manager.compose_directory / Path(self.config.system_name))
        self.the_forest_servers_directory = (server_manager.servers_directory / Path(self.config.system_name))
        self.the_forest_backups_directory = (server_manager.backups_directory / Path(self.config.system_name))

    async def setup(self):
        await self.server_manager.data_manager.create_directory(self.the_forest_compose_directory)
        await self.server_manager.data_manager.create_directory(self.the_forest_servers_directory)
        await self.server_manager.data_manager.create_directory(self.the_forest_backups_directory)


    async def create_server(self, discord_context: dict):
        server_directory_path = (
            self.the_forest_servers_directory /
            discord_context["server_name"]
        )
        compose_directory_path = (
            self.the_forest_compose_directory /
            discord_context["server_name"]
        )
        compose_file = (
            compose_directory_path /
            f"{discord_context["server_name"]}.yml"
        )

        complete_context = {
            **discord_context,
            "server_directory_path": str(server_directory_path),
            "compose_directory_path": str(compose_directory_path),
            "compose_file": str(compose_file)
        }
        try:
            config = self.server_create_config(**complete_context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e

        await self.server_manager.create_server(config.model_dump(), self.config.compose_template)
        
    async def delete_server(self, discord_context: dict):
        server_directory_path = (
            self.the_forest_servers_directory /
            discord_context["server_name"]
        )

        compose_directory_path = (
            self.the_forest_compose_directory /
            discord_context["server_name"]
        )

        complete_contetx = {
            **discord_context,
            "server_directory_path": str(server_directory_path),
            "compose_directory_path": str(compose_directory_path),
            "compose_file": str(compose_directory_path / f"{discord_context["server_name"]}.yml")
        }

        await self.server_manager.delete_server(complete_contetx)

    async def edit_server(self, discord_context: dict):
        if discord_context["server_name"] not in self.get_server_list():
            raise ValueError(f"{discord_context["server_name"]} is not a {self.config.game_name} server or doesn't extist.")

        compose_directory_path = (
            self.the_forest_compose_directory /
            discord_context["server_name"]
        )
        compose_file = (
            compose_directory_path /
            f"{discord_context["server_name"]}.yml"
        )

        complete_context = {
            **discord_context,
            "compose_directory_path": str(compose_directory_path),
            "compose_file": str(compose_file)
        }
        try:
            config = self.server_edit_config(**complete_context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e


        await self.server_manager.edit_server(config.model_dump(exclude_none=True), self.config.compose_template)

    async def reset_server(self, server_name: str):
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a {self.config.game_name} server or doesn't extist.")

        server_directory = self.get_server_directory(server_name)
        complete_context = {
            "server_name": server_name,
            "server_data_directory_paths": []
        }
        for world_directory in self.config.world_directories:
            complete_context["server_data_directory_paths"].append((
                server_directory /
                world_directory
            ))

        await self.server_manager.reset_server(complete_context)

    async def backup_server(self, server_name: str):
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a {self.config.game_name} server or doesn't extist.")

        server_directory = self.get_server_directory(server_name)
        backup_directory = self.get_backup_directory(server_name)

        complete_context = {
            "server_name": server_name,
            "active_data": self.config.world_directories,
            "backup_directory_path": backup_directory,
            "active_directory_path": server_directory,
        }

        await self.server_manager.backup_server(complete_context)

        backups_list = await self.list_backups(server_name)
        while len(backups_list) > self.config.backup_no:
            await self.delete_backup(server_name, min(backups_list))
            backups_list.remove(min(backups_list))

    async def restore_server(self, server_name: str, backup_name: str):
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a {self.config.game_name} server or doesn't extist.")

        server_directory = self.get_server_directory(server_name)
        backup_directory = self.get_backup_directory(server_name)
        complete_context = {
            "server_name": server_name,
            "backup_name": backup_name,
            "active_directory_path": server_directory,
            "backup_directory_path": backup_directory,
        }

        await self.server_manager.restore_server(complete_context)

    async def list_backups(self, server_name: str):
        return self.get_backups(server_name)

    async def delete_backup(self, server_name: str, backup_name: str):

        backup_directory = self.get_backup_directory(server_name)

        if backup_name == "all":
            for backup in await self.list_backups(server_name):
                complete_context = {
                    "server_name": server_name,
                    "backup_name": backup,
                    "backup_directory_path": backup_directory
                }
                await self.server_manager.delete_backup(complete_context)
        else:
            complete_context = {
                "server_name": server_name,
                "backup_name": backup_name,
                "backup_directory_path": backup_directory
            }
            await self.server_manager.delete_backup(complete_context)


    def get_compose_directory(self, server_name: str) -> Path:
        return (self.the_forest_compose_directory / Path(server_name))

    def get_server_directory(self, server_name: str) -> Path:
        return (self.the_forest_servers_directory / Path(server_name))

    def get_backup_directory(self, server_name: str) -> Path:
        return (self.the_forest_backups_directory / Path(server_name))

    def get_server_list(self) -> list[str]:
        servers = []

        for game_directory in Path(self.the_forest_compose_directory).iterdir():
            if not game_directory.is_dir():
                continue

            for compose_file in game_directory.rglob("*.yml"):
                servers.append(compose_file.stem)
        
        return servers

    def get_backups(self, server_name: str) -> list[str]:
        return self.server_manager.backup_manager.get_backups(self.get_backup_directory(server_name))



        

        

        
        