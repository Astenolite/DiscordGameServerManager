from discord.app_commands import Group
from games.abstract.game_command_manager import GameCommandManager

from .ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


from .commands.required.server_create import ArkSurvivalAscendedServerCreate
from .commands.required.server_edit import ArkSurvivalAscendedServerEdit


from .commands.optional.cluster_commands import ClusterCommands
from .commands.optional.mod_commands import ModCommands


class ArkSurvivalAscendedCommandManager(GameCommandManager):

    server_create_class = ArkSurvivalAscendedServerCreate
    server_edit_class = ArkSurvivalAscendedServerEdit

    
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)

        self.cluster_commands = ClusterCommands(self.server_manager)
        self.mod_commands = ModCommands(self.server_manager)



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

        self.cluster_commands.register(game_group)
        self.mod_commands.register(game_group)