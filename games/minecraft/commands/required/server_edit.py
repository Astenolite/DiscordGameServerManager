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
            name="minecraft",
            description=f"Edit a Minecraft server"
        )(self.edit_server)


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

        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.edit_server(context)

            await interaction.followup.send(f"Server `{server_name}` edited successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error editing server: `{e}`")

        