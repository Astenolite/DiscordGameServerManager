import discord

from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.required.server_edit import ServerEdit



class TheForestServerEdit(ServerEdit):

    async def edit_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
        server_steam_account: str | None = None,
        port1: app_commands.Range[int, 1, 65535] | None = None,
        port2: app_commands.Range[int, 1, 65535] | None = None,
        port3: app_commands.Range[int, 1, 65535] | None = None,
        max_players: int | None = None,
        server_password: str | None = None,
        server_admin_password: str | None = None,
        difficulty: Literal[
            "Peaceful",
            "Normal",
            "Hard"
        ] | None = None
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

        await super().edit_server(interaction, context)
