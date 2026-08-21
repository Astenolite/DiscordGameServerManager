from discord.app_commands import Group
from games.abstract.game_command_manager import GameCommandManager

from .ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


from .commands.required.server_create import ArkSurvivalAscendedServerCreate
from .commands.required.server_edit import ArkSurvivalAscendedServerEdit
from games.abstract.commands.required.server_delete import ServerDelete
from games.abstract.commands.required.server_reset import ServerReset
from games.abstract.commands.required.server_backup import ServerBackup
from games.abstract.commands.required.server_list_backups import ServerListBackups
from games.abstract.commands.required.server_restore import ServerRestore
from games.abstract.commands.required.server_delete_backup import ServerDeleteBackup


from .commands.optional.cluster_commands import ClusterCommands
from .commands.optional.mod_commands import ModCommands


class ArkSurvivalAscendedCommandManager(GameCommandManager):

    server_create_class = ArkSurvivalAscendedServerCreate
    server_delete_class = ServerDelete
    server_edit_class = ArkSurvivalAscendedServerEdit
    server_reset_class = ServerReset
    server_backup_class = ServerBackup
    server_restore_class = ServerRestore
    server_delete_backup_class = ServerDeleteBackup
    server_list_backups_class = ServerListBackups

    
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)

        self.cluster_commands = ClusterCommands(self.server_manager)
        self.mod_commands = ModCommands(self.server_manager)



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

        self.cluster_commands.register(game_group)
        self.mod_commands.register(game_group)