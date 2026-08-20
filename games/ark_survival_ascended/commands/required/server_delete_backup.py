import traceback
import discord

from discord.app_commands import Group

from games.abstract.commands.commands import Commands


from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ServerDeleteBackup(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="ark-survival-ascended",
            description="Delete the backup of an Ark Survival Ascended server"
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

        