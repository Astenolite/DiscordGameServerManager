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
            name="minecraft",
            description=f"Create a Minecraft server"
        )(self.create_server)


    async def create_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
        port: app_commands.Range[int, 1, 65535] = 25565,
        server_type: Literal[
            "VANILLA",
            "SPIGOT",
            "FABRIC",
            "FORGE",
            "PAPER",
        ] = "VANILLA",
        version: str = "LATEST",
        memory: app_commands.Range[int, 1, None] = 4,
        max_players: app_commands.Range[int, 1, None] = 10,
        online_mode: bool = True,
        difficulty: Literal[
            "peaceful",
            "easy",
            "normal",
            "hard",
        ] = "normal",
        render_distance: app_commands.Range[int, 4, 64] = 16,
    ): 
        context = {
            "server_name": server_name,
            "port": port,
            "server_type": server_type,
            "version": version,
            "memory": memory,
            "max_players": max_players,
            "online_mode": online_mode,
            "difficulty": difficulty,
            "render_distance": render_distance
        }

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.create_server(context)

            await interaction.followup.send(f"Server `{server_name}` created and started successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error creating server: `{e}`")

        