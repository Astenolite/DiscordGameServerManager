from discord.app_commands import Group
from games.abstract.game_command_manager import GameCommandManager

from .minecraft_server_manager import MinecraftServerManager


from .commands.required.server_create import MinecraftServerCreate
from .commands.required.server_edit import MinecraftServerEdit

from .commands.optional.minecraft_commands import MinecraftCommands


class MinecraftCommandManager(GameCommandManager):

    server_create_class = MinecraftServerCreate
    server_edit_class = MinecraftServerEdit

    
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)

        self.game_commands = MinecraftCommands(server_manager)


    def register_commands(self,
        game_group: Group,
        create_group: Group,
        edit_group: Group,
    ):

        super().register_commands(
            game_group=game_group,
            create_group=create_group,
            edit_group=edit_group,
        )

        self.game_commands.register(game_group)