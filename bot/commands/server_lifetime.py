import discord
import traceback
from discord.ext import commands



class ServerLifetimeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_manager = bot.server_manager

    def register(self):
        self.bot.server_group.command(
            name="start",
            description="Start server"
        )(self.start_server)

        self.bot.server_group.command(
            name="restart",
            description="Restart server"
        )(self.restart_server)

        self.bot.server_group.command(
            name="stop",
            description="Stop server"
        )(self.stop_server)

        self.bot.server_group.command(
            name="delete",
            description="Delete server"
        )(self.delete_server)

        self.bot.server_group.command(
            name="reset",
            description="Reset server"
        )(self.reset_server)
    
    async def start_server(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)
    
        try:
            await self.server_manager.start_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` started successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error starting server: `{e}`")

    async def restart_server(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.restart_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` restared sucessfully")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error restarting server: `{e}`")

    async def stop_server(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.stop_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` stoped sucessfully")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error stoping server: `{e}`")


    async def delete_server(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)
        
        try:
            self.server_manager.delete_server(server_name)
            await interaction.followup.send(f"Server `{server_name}` sucessfully deleted")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error deleting server: `{e}`")

    async def reset_server(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)
        
        try:
            self.server_manager.reset_server(server_name)
            await interaction.followup.send(f"Server `{server_name}` sucessfully reseted")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error reseting server: `{e}`")

    
        
async def setup(bot):
    cog = ServerLifetimeCommands(bot)

    cog.register()

    await bot.add_cog(cog)
