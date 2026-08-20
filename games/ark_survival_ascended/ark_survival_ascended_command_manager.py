from discord import app_commands
from discord.app_commands import Group
from games.abstract.game_command_manager import GameCommandManager

from .ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager
from .config.ark_survival_ascended_config import ArkSurvivalAscendedConfig


from .commands.required.server_create import ServerCreate
from .commands.required.server_delete import ServerDelete
from .commands.required.server_edit import ServerEdit
from .commands.required.server_reset import ServerReset
from .commands.required.server_backup import ServerBackup
from .commands.required.server_list_backups import ServerListBackups
from .commands.required.server_restore import ServerRestore
from .commands.required.server_delete_backup import ServerDeleteBackup


from .commands.optional.cluster_commands import ClusterCommands
from .commands.optional.mod_commands import ModCommands



class ArkSurvivalAscendedCommandManager(GameCommandManager):
    config = ArkSurvivalAscendedConfig

    def __init__(
            self, 
            server_manager: ArkSurvivalAscendedServerManager,
        ):
            super().__init__(server_manager)

            self.server_create = ServerCreate(self.server_manager)
            self.server_delete = ServerDelete(self.server_manager)
            self.server_edit = ServerEdit(self.server_manager)
            self.server_reset = ServerReset(self.server_manager)
            self.server_backup = ServerBackup(self.server_manager)
            self.server_restore = ServerRestore(self.server_manager)
            self.server_list_backups = ServerListBackups(self.server_manager)
            self.server_delete_backup = ServerDeleteBackup(self.server_manager)

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
        self.server_create.register(create_group)
        self.server_delete.register(delete_group)
        self.server_edit.register(edit_group)
        self.server_reset.register(reset_group)
        self.server_backup.register(backup_group)
        self.server_restore.register(restore_group)
        self.server_list_backups.register(list_backups_group)
        self.server_delete_backup.register(delete_backup_group)

        self.cluster_commands.register(game_group)
        self.mod_commands.register(game_group)