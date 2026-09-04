from abc import ABC, abstractmethod
from pathlib import Path

from core.docker_manager import DockerManager
from core.compose_manager import ComposeManager
from core.data_manager import DataManager
from core.server_registry import ServerRegistry

from .config.game_server_create_config import GameServerCreateConfig
from .config.game_server_edit_config import GameServerEditConfig
from .config.game_config import GameConfig


class GameServerManager(ABC):
    config: type[GameConfig]
    server_create_config: type[GameServerCreateConfig]
    server_edit_config: type[GameServerEditConfig]

    # Sets the server_manager and the game specific workspace directories
    def __init__(
        self,
        docker_manager: DockerManager,
        compose_manager: ComposeManager,
        data_manager: DataManager,
        server_registry: ServerRegistry,
        compose_directory: str,
        containers_directory: str,
        backups_directory: str,
    ):
        self.docker_manager = docker_manager
        self.compose_manager = compose_manager
        self.data_manager = data_manager
        self.server_registry = server_registry
        
        self.compose_directory = compose_directory / self.config.system_name
        self.containers_directory = containers_directory / self.config.system_name
        self.backups_directory = backups_directory / self.config.system_name

    # Creates the root directories of the workspace
    async def setup(self):
        await self.data_manager.create_directory(self.compose_directory)
        await self.data_manager.create_directory(self.containers_directory)
        await self.data_manager.create_directory(self.backups_directory)

    async def get_compose_directory(self, server_name: str) -> Path:
        return self.compose_directory / server_name

    async def get_container_directory(self, server_name: str) -> Path:
        return self.containers_directory / server_name

    async def get_backup_directory(self, server_name: str) -> Path:
        return self.backups_directory / server_name


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
        await self.server_type_check(context["server_name"])
        await self.nonexistence_check(context["server_name"])

        try:
            config = self.server_create_config(**context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e

        try:
            self.compose_manager.render(
                template_path=str(context["model_path"]),
                output_path=Path(context["compose_file"]),
                context=config
            )
            await self.docker_manager.compose_up(context["compose_file"])

        except Exception as e:
            if Path(context["compose_file"]).exists():
                try:
                    self.docker_manager.compose_down(context["compose_file"])
                except Exception:
                    pass

            self.data_manager.delete_directory(Path(context["compose_directory_path"]))
            self.data_manager.delete_directory(Path(context["container_directory_path"]))

            raise ValueError("Server could not be created.") from e
    

    # Edits a server
    @abstractmethod
    async def edit_server(self, context: dict) -> None:
        await self.existence_check(context["server_name"])
        await self.container_check(context["server_name"])
        await self.offline_check(context["server_name"])

        try:
            config = self.server_edit_config(**context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e
        
        try:
            self.compose_manager.edit(
                template_path=str(context["model_path"]),
                existing_file=Path(context["compose_file"]),
                new_context=config
            )
            await self.docker_manager.compose_up(context["compose_file"])
        except Exception as e:
            raise ValueError("Server could not be edited.") from e
        await self.server_type_check(context["server_name"])

        

        
        