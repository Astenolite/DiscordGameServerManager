import traceback
import discord

from discord.app_commands import Group
from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.commands import Commands

from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ServerEdit(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="ark-survival-ascended",
            description=f"Edit an Ark Survival Ascended server"
        )(self.edit_server)


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

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.edit_server(context)

            await interaction.followup.send(f"Server `{server_name}` edited successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error editing server: `{e}`")

        