import discord

from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.required.server_create import ServerCreate



class MinecraftServerCreate(ServerCreate):

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

        await super().create_server(interaction, context)

        