import discord

from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.required.server_create import ServerCreate


class TheForestServerCreate(ServerCreate):


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

        await super().create_server(interaction, context)

        