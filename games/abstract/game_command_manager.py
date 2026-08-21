from discord.app_commands import Group
from abc import ABC

from typing import ClassVar

from .game_server_manager import GameServerManager

from .commands.required.server_create import ServerCreate
from .commands.required.server_delete import ServerDelete
from .commands.required.server_edit import ServerEdit
from .commands.required.server_reset import ServerReset
from .commands.required.server_backup import ServerBackup
from .commands.required.server_restore import ServerRestore
from .commands.required.server_delete_backup import ServerDeleteBackup
from .commands.required.server_list_backups import ServerListBackups

class GameCommandManager(ABC):

    server_create_class: ClassVar[type[ServerCreate]]
    server_delete_class: ClassVar[type[ServerDelete]]
    server_edit_class: ClassVar[type[ServerEdit]]
    server_reset_class: ClassVar[type[ServerReset]]
    server_backup_class: ClassVar[type[ServerBackup]]
    server_restore_class: ClassVar[type[ServerRestore]]
    server_delete_backup_class: ClassVar[type[ServerDeleteBackup]]
    server_list_backups_class: ClassVar[type[ServerListBackups]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Attributes that must themselves be classes derived from a base class
        required_classes = {
            "server_create_class": ServerCreate,
            "server_delete_class": ServerDelete,
            "server_edit_class": ServerEdit,
            "server_reset_class": ServerReset,
            "server_backup_class": ServerBackup,
            "server_restore_class": ServerRestore,
            "server_delete_backup_class": ServerDeleteBackup,
            "server_list_backups_class": ServerListBackups
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
        self.server_delete = self.server_delete_class(server_manager)
        self.server_edit = self.server_edit_class(server_manager)
        self.server_reset = self.server_reset_class(server_manager)
        self.server_backup = self.server_backup_class(server_manager)
        self.server_restore = self.server_restore_class(server_manager)
        self.server_delete_backup = self.server_delete_backup_class(server_manager)
        self.server_list_backups = self.server_list_backups_class(server_manager)


    # register required command classes
    def register_commands(self,
        game_group: Group,
        create_group: Group,
        delete_group: Group,
        edit_group: Group,
        backup_group: Group,
        restore_group: Group,
        list_backups_group: Group,
        delete_backup_group: Group,
        reset_group: Group,
    ):
        self.server_create.register(create_group)
        self.server_delete.register(delete_group)
        self.server_edit.register(edit_group)
        self.server_reset.register(reset_group)
        self.server_backup.register(backup_group)
        self.server_restore.register(restore_group)
        self.server_list_backups.register(list_backups_group)
        self.server_delete_backup.register(delete_backup_group)



