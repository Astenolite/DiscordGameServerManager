import discord

from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.required.server_create import ServerCreate

class ArkSurvivalAscendedServerCreate(ServerCreate):


    async def create_server(
        self,
        interaction: discord.Interaction,
        cluster_name: str,
        server_name: str,
        game_port: app_commands.Range[int, 1, 65535] = 7777,
        steam_port: app_commands.Range[int, 1, 65535] = 27015,
        map_name: Literal[
            "TheIsland_WP",
            "ScorchedEarth_WP",
            "TheCenter_WP",
            "Aberration_WP",
            "Extinction_WP",
            "Ragnarok_WP",
            "Astraeos_WP",
            "Valguero_WP",
            "LostColony_WP",
            "Genessis_WP",
        ] = "TheIsland_WP",
        max_players: app_commands.Range[int, 1, 50] = 5,
    ):
        context = {
            "cluster_name": cluster_name,
            "server_name": server_name,
            "game_port": game_port,
            "steam_port": steam_port,
            "map_name": map_name,
            "max_players": max_players,
        }

        await super().create_server(interaction, context)

        