import traceback
import discord

from discord.app_commands import Group
from discord import app_commands
from typing_extensions import Literal

from games.abstract.commands.commands import Commands

from games.minecraft.minecraft_server_manager import MinecraftServerManager


class ServerEdit(Commands):
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="the-forest",
            description=f"Edit a The Forest server"
        )(self.edit_server)

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

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.edit_server(context)

            await interaction.followup.send(
                f"Server `{server_name}` edited successfully."
            )

        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(
                f"Error editing server: `{e}`"
            )

    