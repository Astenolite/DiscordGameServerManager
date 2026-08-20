import traceback
import discord

from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.minecraft.minecraft_server_manager import MinecraftServerManager


class ServerReset(Commands):
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="minecraft",
            description=f"Reset the world of a Minecraft server"
        )(self.reset_server)


    async def reset_server(
        self,
        interaction: discord.Interaction,
        server_name: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.reset_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` reseted successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error reseting server: `{e}`")

        