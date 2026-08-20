import traceback
import discord

from discord.app_commands import Group
from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.commands import Commands

from games.minecraft.minecraft_server_manager import MinecraftServerManager


class ServerDelete(Commands):
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="the-forest",
            description=f"Delete a The Forest server"
        )(self.delete_server)


    async def delete_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
    ): 
        context = {
            "server_name": server_name,
        }

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.delete_server(context)

            await interaction.followup.send(f"Server `{server_name}` deleted successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error deleting server: `{e}`")

        