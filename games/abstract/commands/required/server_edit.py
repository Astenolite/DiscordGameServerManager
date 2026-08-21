import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerEdit(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Edit a(n) {self.game_name} server"
        )(self.edit_server)


    async def edit_server(self, interaction: discord.Interaction, context: dict):
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.edit_server(context)

            await interaction.followup.send(f"Server `{context["server_name"]}` edited successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error editing server: `{e}`")

        