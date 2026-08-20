import traceback
import discord

from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ServerBackup(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="ark-survival-ascended",
            description=f"Backup the world of an Ark Survival Ascended server"
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

        