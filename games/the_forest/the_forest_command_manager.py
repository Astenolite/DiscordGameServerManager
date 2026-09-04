from games.abstract.game_command_manager import GameCommandManager


from .commands.required.server_create import TheForestServerCreate
from .commands.required.server_edit import TheForestServerEdit


class TheForestCommandManager(GameCommandManager):

    server_create_class = TheForestServerCreate
    server_edit_class = TheForestServerEdit
        