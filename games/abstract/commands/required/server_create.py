import traceback
import discord

from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerCreate(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"Create a(n) {self.game_name} server"
        )(self.create_server)


    async def create_server(self, interaction: discord.Interaction, context: dict):
        await interaction.response.defer(thinking=True)
        try:
            await self.server_manager.create_server(context)

            await interaction.followup.send(f"Server `{context["server_name"]}` created successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error creating server: `{e}`")

        