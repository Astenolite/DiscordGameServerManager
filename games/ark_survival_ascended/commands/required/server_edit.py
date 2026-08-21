import discord

from discord import app_commands
from games.abstract.commands.required.server_edit import ServerEdit


class ArkSurvivalAscendedServerEdit(ServerEdit):


    async def edit_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
        game_port: app_commands.Range[int, 1, 65535] | None = None,
        steam_port: app_commands.Range[int, 1, 65535] | None = None,
        max_players: app_commands.Range[int, 1, 50] | None = None,
    ):
        context = {
            "server_name": server_name,
            "game_port": game_port,
            "steam_port": steam_port,
            "max_players": max_players,
        }

        await super().edit_server(interaction, context)

        