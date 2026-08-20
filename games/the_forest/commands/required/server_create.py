import traceback
import discord

from discord.app_commands import Group
from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.commands import Commands

from games.minecraft.minecraft_server_manager import MinecraftServerManager


class ServerCreate(Commands):
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="the-forest",
            description=f"Create a The Forest server"
        )(self.create_server)


    async def create_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
        server_steam_account: str,
        port1: app_commands.Range[int, 1, 65535] = 8766,
        port2: app_commands.Range[int, 1, 65535] = 27015,
        port3: app_commands.Range[int, 1, 65535] = 27016,
        max_players: int = 5,
        server_password: str = "",
        server_admin_password: str = "admin",
        difficulty: Literal[
            "Peaceful",
            "Normal",
            "Hard"
        ] = "Normal"
    ): 
        context = {
            "server_name": server_name,
            "server_steam_account": server_steam_account,
            "port1": port1,
            "port2": port2,
            "port3": port3,
            "max_players": max_players,
            "server_password": server_password,
            "server_admin_password": server_admin_password,
            "difficulty": difficulty
        }

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.create_server(context)

            await interaction.followup.send(f"Server `{server_name}` created and started successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error creating server: `{e}`")

        