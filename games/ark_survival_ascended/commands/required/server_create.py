import traceback
import discord

from discord.app_commands import Group
from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.commands import Commands

from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ServerCreate(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="ark-survival-ascended",
            description=f"Create an Ark Survival Ascended server"
        )(self.create_server)


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

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.create_server(context)

            await interaction.followup.send(f"Server `{server_name}` created and started successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error creating server: `{e}`")

        