from discord.app_commands import Group
from abc import ABC, abstractmethod

from .game_server_manager import GameServerManager
from .config.game_config import GameConfig


class GameCommandManager(ABC):

    config: type[GameConfig]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Attributes that must themselves be classes derived from a base class
        required_classes = {
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

    # intialize all command classes
    @abstractmethod
    def __init__(
        self, 
        server_manager: GameServerManager
    ):
        self.server_manager = server_manager

    # register all command classes
    @abstractmethod
    def register_commands(self,
        game_group: Group,
        create_group: Group,
        delete_group: Group,
        edit_group: Group,
        backup_group: Group,
        list_backups_group: Group,
        delete_backup_group: Group,
        restore_group: Group,
        reset_group: Group,
    ):
        ...