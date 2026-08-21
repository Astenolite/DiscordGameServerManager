import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerBackup(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Backup the world of an {self.game_name} server"
        )(self.backup_server)

    async def backup_server(
        self,
        interaction: discord.Interaction,
        server_name: str
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.backup_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` backed up successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error backing up server: `{e}`")

        