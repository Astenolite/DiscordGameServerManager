import traceback
import discord

from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.minecraft.minecraft_server_manager import MinecraftServerManager


class ServerDeleteBackup(Commands):
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="the-forest",
            description="Delete the backup of a The Forest server (use `all` for full deletion)"
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

            await interaction.followup.send(f"Backup deleted successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error restoring server: `{e}`")

        