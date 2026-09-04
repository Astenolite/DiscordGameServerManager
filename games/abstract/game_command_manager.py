from discord.app_commands import Group
from abc import ABC

from typing import ClassVar

from .game_server_manager import GameServerManager

from .commands.required.server_create import ServerCreate
from .commands.required.server_edit import ServerEdit

class GameCommandManager(ABC):

    server_create_class: ClassVar[type[ServerCreate]]
    server_edit_class: ClassVar[type[ServerEdit]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Attributes that must themselves be classes derived from a base class
        required_classes = {
            "server_create_class": ServerCreate,
            "server_edit_class": ServerEdit,
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

    # intialize required command classes
    def __init__(
        self, 
        server_manager: GameServerManager
    ):
        self.server_manager = server_manager

        self.server_create = self.server_create_class(server_manager)
        self.server_edit = self.server_edit_class(server_manager)


    # register required command classes
    def register_commands(self,
        game_group: Group,
        create_group: Group,
        edit_group: Group,
    ):
        self.server_create.register(create_group)
        self.server_edit.register(edit_group)



