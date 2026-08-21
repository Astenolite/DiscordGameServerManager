import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerDeleteBackup(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Delete the backup of a(n) {self.game_name} server"
        )(self.delete_backup)

    async def delete_backup(
        self,
        interaction: discord.Interaction,
        server_name: str,
        backup_name: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.delete_backup(server_name, backup_name)

            await interaction.followup.send(f"Backup {backup_name} of {server_name} deleted successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error deleting backup: `{e}`")
    

        