import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerDelete(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Delete a(n) {self.game_name} server"
        )(self.delete_server)


    async def delete_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
    ): 

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.delete_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` deleted successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error deleting server: `{e}`")

        