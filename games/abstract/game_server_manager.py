from abc import ABC, abstractmethod
from pathlib import Path

from core.server_manager import ServerManager

from .config.game_server_create_config import GameServerCreateConfig
from .config.game_server_edit_config import GameServerEditConfig
from .config.game_config import GameConfig


class GameServerManager(ABC):
    config: type[GameConfig]
    server_create_config: type[GameServerCreateConfig]
    server_edit_config: type[GameServerEditConfig]

    # Makes sure that mandatory attributes are present and of the correct types
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        required_classes = {
            "server_create_config": GameServerCreateConfig,
            "server_edit_config": GameServerEditConfig,
            "config": GameConfig
        }

        for name, expected_base in required_classes.items():
            if name not in cls.__dict__:
                raise TypeError(
                    f"{cls.__name__} must define {name!r}"
                )

            value = getattr(cls, name)

            if not isinstance(value, type):
                raise TypeError(
                    f"{cls.__name__}.{name} must be a class"
                )

            if not issubclass(value, expected_base):
                raise TypeError(
                    f"{cls.__name__}.{name} must be a subclass of "
                    f"{expected_base.__name__}"
                )

    # Sets the server_manager and the game specific workspace directories
    def __init__(
        self,
        server_manager: ServerManager,
    ):
        self.server_manager = server_manager
        
        self.compose_directory = server_manager.compose_directory / self.config.system_name
        self.containers_directory = server_manager.containers_directory / self.config.system_name
        self.backups_directory = server_manager.backups_directory / self.config.system_name

    # Creates the root directories of the workspace
    async def setup(self):
        await self.server_manager.data_manager.create_directory(self.compose_directory)
        await self.server_manager.data_manager.create_directory(self.containers_directory)
        await self.server_manager.data_manager.create_directory(self.backups_directory)

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
        

    # Creates a server
    @abstractmethod
    async def create_server(self, context: dict) -> None:
        try:
            config = self.server_create_config(**context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e

        await self.server_manager.create_server(config.model_dump(), self.config.compose_template)

    # Deletes a server 
    @abstractmethod
    async def delete_server(self, context: dict) -> None:
        await self.server_type_check(context["server_name"])
        await self.server_manager.delete_server(context)

    # Edits a server
    @abstractmethod
    async def edit_server(self, context: dict) -> None:
        await self.server_type_check(context["server_name"])

        try:
            config = self.server_edit_config(**context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e

        await self.server_manager.edit_server(config.model_dump(exclude_none=True), self.config.compose_template)

    # Resets the world of a server
    @abstractmethod
    async def reset_server(self, server_name: str, server_container_directory: str) -> None:
        context = {
            "server_name": server_name,
            "server_data_directory_paths": []
        }
        for world_directory in self.config.world_directories:
            context["server_data_directory_paths"].append((
                server_container_directory /
                world_directory
            ))

        await self.server_manager.reset_server(context)

    # Backs up the world of a server
    @abstractmethod
    async def backup_server(self, server_name: str, server_container_directory: str, server_backup_directory: str) -> None:
        context = {
            "server_name": server_name,
            "active_data": self.config.world_directories,
            "backup_directory_path": server_backup_directory,
            "active_directory_path": server_container_directory,
        }

        await self.server_manager.backup_server(context)

        backups_list = await self.list_backups(server_name)
        
        while len(backups_list) > self.config.backup_no:
            await self.delete_backup(server_name, min(backups_list))
            backups_list.remove(min(backups_list))

    # Restores the server state from a backup
    @abstractmethod
    async def restore_server(self, server_name: str, backup_name: str, server_container_directory: str, server_backup_directory: str) -> None:
        context = {
            "server_name": server_name,
            "backup_name": backup_name,
            "active_directory_path": server_container_directory,
            "backup_directory_path": server_backup_directory,
        }

        await self.server_manager.restore_server(context)

    # Lists backups of a server
    @abstractmethod 
    async def list_backups(self, server_name: str) -> None:
        ...

    # Delete one or all backups
    @abstractmethod
    async def delete_backup(self, server_name: str, backup_directory_path: str, backup_name) -> None:
        if backup_name == "all":
            for backup in await self.list_backups(server_name):
                context = {
                    "backup_name": backup,
                    "backup_directory_path": backup_directory_path
                }
                await self.server_manager.delete_backup(context)
        else:
            complete_context = {
                "backup_name": backup_name,
                "backup_directory_path": backup_directory_path
            }
            await self.server_manager.delete_backup(complete_context)

        

        
        