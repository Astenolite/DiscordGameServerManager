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

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Attributes that must themselves be classes derived from a base class
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
    

    @abstractmethod
    def __init__(
        self,
        server_manager: ServerManager,
    ):
        ...

    @abstractmethod
    async def setup(self):
        ...

    @abstractmethod
    def get_compose_directory(self, server_name: str) -> Path:
        ...

    @abstractmethod
    def get_server_directory(self, server_name: str) -> Path:
        ...

    @abstractmethod
    def get_backup_directory(self, server_name: str)-> Path:
        ...

        

        
        