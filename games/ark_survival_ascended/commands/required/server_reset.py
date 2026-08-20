import traceback
import discord

from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ServerReset(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="ark-survival-ascended",
            description=f"Reset the world of an Ark Survival Ascended server"
        )(self.reset_server)


    async def reset_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.reset_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` reseted successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error reseting server: `{e}`")

        