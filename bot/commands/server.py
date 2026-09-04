import discord
import traceback
from discord import app_commands
from discord.ext import commands


def embeded_status(server_name: str, status: dict):
    if not status["running"]:
        color = discord.Color.light_grey()
        status_icon = "⚪"
        status_text = "Offline"
        health_icon = "⚪"
        health_text = "Offline"
    elif status["health"] == "healthy":
        color = discord.Color.green()
        status_icon = "🟢"
        status_text = "Running"
        health_icon = "✅"
        health_text = "Healthy"
    elif status["health"] == "starting":
        color = discord.Color.yellow()
        status_icon = "🟡"
        status_text = "Starting"
        health_icon = "🟡"
        health_text = "Starting"
    elif status["health"] == "unhealthy":
        color = discord.Color.red()
        status_icon = "🔴"
        status_text = "Running"
        health_icon = "❌"
        health_text = "Unhealthy"
    else:
        color = discord.Color.green()
        status_icon = "🟢"
        status_text = "Running"
        health_icon = "➖"
        health_text = "No healthcheck"

    embed = discord.Embed(
        title=f"🖥️ {server_name}",
        color=color,
    )

    embed.add_field(
        name="Status",
        value=f"{status_icon} {status_text}",
        inline=True,
    )

    if status["running"]:
        embed.add_field(
            name="Health",
            value=f"{health_icon} {health_text}",
            inline=True,
        )

        embed.add_field(
            name="Online Since",
            value=(
                f"<t:{status['started_at']}:F>\n"
                f"<t:{status['started_at']}:R>"
            ),
            inline=False,
        )

    else:
        if status.get("finished_at"):
            embed.add_field(
                name="Offline Since",
                value=(
                    f"<t:{status['finished_at']}:F>\n"
                    f"<t:{status['finished_at']}:R>"
                ),
                inline=False,
            )

    embed.add_field(
        name="Last update",
        value=f"<t:{status['created']}:F>",
        inline=False,
    )

    return embed

def embeded_servers(servers: list):
    embed = discord.Embed(
        title="🖥️ Game Servers",
        description=f"{len(servers)} server(s) available",
        color=discord.Color.blue(),
    )

    games = {}

    for server_name, game in servers:
        games.setdefault(game, []).append(server_name)

    for game, server_names in games.items():
        server_list = "\n".join(
            f"• {server_name}"
            for server_name in server_names
        )

        embed.add_field(
            name=f"{game}",
            value=server_list,
            inline=False,
        )

    return embed

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_manager = bot.server_manager

    def register(self):
        self.bot.server_group.command(
            name="list",
            description="List all servers"
        )(self.list_servers)

        self.bot.server_group.command(
            name="game",
            description="Get game of server"
        )(self.get_game)


    async def list_servers(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        try:
            servers = await self.server_manager.list_servers()

            if not servers:
                await interaction.followup.send("No servers found.")
                return

            embed = embeded_servers(servers)

            await interaction.followup.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error getting servers: `{e}`")

    async def get_game(self, interaction: discord.Interaction, server_name:str):
        await interaction.response.defer(thinking=True)
        try:
            game = await self.server_manager.get_game(server_name)

            await interaction.followup.send(f"Server `{server_name}` is a **{game}** server")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error establishing nature of server: `{e}`")

        
async def setup(bot):
    cog = ServerCommands(bot)

    cog.register()

    await bot.add_cog(cog)
