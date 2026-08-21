from games.abstract.game_command_manager import GameCommandManager


from .commands.required.server_create import TheForestServerCreate
from .commands.required.server_edit import TheForestServerEdit
from games.abstract.commands.required.server_delete import ServerDelete
from games.abstract.commands.required.server_reset import ServerReset
from games.abstract.commands.required.server_backup import ServerBackup
from games.abstract.commands.required.server_list_backups import ServerListBackups
from games.abstract.commands.required.server_restore import ServerRestore
from games.abstract.commands.required.server_delete_backup import ServerDeleteBackup



class TheForestCommandManager(GameCommandManager):

    server_create_class = TheForestServerCreate
    server_delete_class = ServerDelete
    server_edit_class = TheForestServerEdit
    server_reset_class = ServerReset
    server_backup_class = ServerBackup
    server_restore_class = ServerRestore
    server_delete_backup_class = ServerDeleteBackup
    server_list_backups_class = ServerListBackups
        