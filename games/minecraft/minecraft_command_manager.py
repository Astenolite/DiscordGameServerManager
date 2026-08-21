from discord.app_commands import Group
from games.abstract.game_command_manager import GameCommandManager

from .minecraft_server_manager import MinecraftServerManager


from .commands.required.server_create import MinecraftServerCreate
from .commands.required.server_edit import MinecraftServerEdit
from games.abstract.commands.required.server_delete import ServerDelete
from games.abstract.commands.required.server_reset import ServerReset
from games.abstract.commands.required.server_backup import ServerBackup
from games.abstract.commands.required.server_list_backups import ServerListBackups
from games.abstract.commands.required.server_restore import ServerRestore
from games.abstract.commands.required.server_delete_backup import ServerDeleteBackup

from .commands.optional.minecraft_commands import MinecraftCommands


class MinecraftCommandManager(GameCommandManager):

    server_create_class = MinecraftServerCreate
    server_delete_class = ServerDelete
    server_edit_class = MinecraftServerEdit
    server_reset_class = ServerReset
    server_backup_class = ServerBackup
    server_restore_class = ServerRestore
    server_delete_backup_class = ServerDeleteBackup
    server_list_backups_class = ServerListBackups

    
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)

        self.game_commands = MinecraftCommands(server_manager)


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

        super().register_commands(
            game_group=game_group,
            create_group=create_group,
            delete_group=delete_group,
            edit_group=edit_group,
            backup_group=backup_group,
            restore_group=restore_group,
            list_backups_group=list_backups_group,
            delete_backup_group=delete_backup_group,
            reset_group=reset_group
        )

        self.game_commands.register(game_group)