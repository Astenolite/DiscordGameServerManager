import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerReset(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Reset the world of a(n) {self.game_name} server"
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

        