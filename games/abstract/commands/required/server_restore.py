import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerRestore(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Restore the world of a(n) {self.game_name} server from a backup"
        )(self.restore_server)


    async def restore_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
        backup_name: str = None,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.restore_server(server_name, backup_name)

            await interaction.followup.send(f"Server `{server_name}` restored successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error restoring server: `{e}`")

        