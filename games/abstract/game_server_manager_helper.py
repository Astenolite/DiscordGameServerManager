from abc import ABC
from pathlib import Path


from .config.game_config import GameConfig


class GameServerManagerHelper(ABC):
    config: type[GameConfig]

    # Sets the server_manager and the game specific workspace directories
    def __init__(
        self,
        compose_directory: Path,
        containers_directory: Path,
        backups_directory: Path,
    ):
        self.compose_directory = compose_directory / self.config.system_name
        self.containers_directory = containers_directory / self.config.system_name
        self.backups_directory = backups_directory / self.config.system_name

    """
    TODO
    # Creates the root directories of the workspace
    async def setup(self):
        await self.server_manager.data_manager.create_directory(self.compose_directory)
        await self.server_manager.data_manager.create_directory(self.containers_directory)
        await self.server_manager.data_manager.create_directory(self.backups_directory)
    """ 

    # throws error if server game is not the same as manager game
    async def server_type_check(self, server_name: str) -> None:
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a(n) {self.config.game_name} server or doesn't exist.")

    # Constructs a list with the name of all *.yml files in the compose directory
    def get_server_list(self) -> list[str]:
        servers = []

        for game_directory in Path(self.compose_directory).iterdir():
            if not game_directory.is_dir():
                continue

            for compose_file in game_directory.rglob("*.yml"):
                servers.append(compose_file.stem)
        
        return servers


    async def get_compose_directory(self, server_name: str) -> Path:
        return self.compose_directory / server_name

    async def get_container_directory(self, server_name: str) -> Path:
        return self.containers_directory / server_name

    async def get_backup_directory(self, server_name: str) -> Path:
        return self.backups_directory / server_name

    async def get_world_directories(self, server_name: str) -> list[Path]:
        server_container_directory = await self.get_container_directory(server_name)
        world_directory_list = []

        for world_directory in self.config.world_directories:
            world_directory_list.append(server_container_directory / world_directory)

        return world_directory_list

    async def get_compose_file(self, server_name: str) -> Path:
        server_compose_directory = await self.get_compose_directory(server_name)
        return server_compose_directory / server_name / f"{server_name}.yml"
    

    # Deletes a server
    async def delete_server(self, server_name: str) -> dict:
        await self.server_type_check(server_name)

        context = {
            "compose_file": await self.get_compose_file(server_name),
            "compose_directory_path": await self.get_compose_directory(server_name),
            "container_directory_path": await self.get_container_directory(server_name),
        }

        return context

    # Resets the world of a server
    async def reset_server(self, server_name: str) -> dict:
        await self.server_type_check(server_name)

        context = {
            "server_name": server_name,
            "server_data_directory_paths": await self.get_world_directories(server_name)
        }

        return context

    # Backs up the world of a server
    async def backup_server(self, server_name: str) -> dict:
        await self.server_type_check(server_name)
        
        context = {
            "server_name": server_name,
            "active_data": self.config.world_directories,
            "backup_directory_path": await self.get_backup_directory(server_name),
            "active_directory_path": await self.get_container_directory(server_name),
            "max_backups": self.config.backup_no, 
        }

        return context

    # Restores the server state from a backup
    async def restore_server(self, server_name: str, backup_name: str) -> dict:
        await self.server_type_check(server_name)

        context = {
            "server_name": server_name,
            "backup_name": backup_name,
            "backup_directory_path": await self.get_backup_directory(server_name),
            "active_directory_path": await self.get_container_directory(server_name),
        }

        return context

    async def delete_backup(self, server_name: str, backup_name: str) -> dict:
        await self.server_type_check(server_name)

        context = {
            "server_name": server_name,
            "backup_name": backup_name,
            "backup_directory_path": await self.get_backup_directory(server_name),
        }

        return context

    async def list_backups(self, server_name: str) -> dict:
        await self.server_type_check(server_name)
        context = {
            "backup_directory_path": await self.get_backup_directory(server_name),
        }
        return context


        
        