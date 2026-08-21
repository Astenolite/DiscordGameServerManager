import discord

from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.required.server_edit import ServerEdit


class MinecraftServerEdit(ServerEdit):

    async def edit_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
        port: app_commands.Range[int, 1, 65535] | None = None,
        server_type: Literal[
            "VANILLA",
            "SPIGOT",
            "FABRIC",
            "FORGE",
            "PAPER",
        ] | None = None,
        version: str | None = None,
        memory: app_commands.Range[int, 1, None] | None = None,
        max_players: app_commands.Range[int, 1, None] | None = None,
        online_mode: bool | None = None,
        difficulty: Literal[
            "peaceful",
            "easy",
            "normal",
            "hard",
        ] | None = None,
        render_distance: app_commands.Range[int, 4, 64] | None = None,
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

        await super().edit_server(interaction, context)

        