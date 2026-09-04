import discord
from discord.ext import commands
from discord.app_commands import Group

from games.registry import GAME_REGISTRY

class GameServerManagerBot(commands.Bot):
    def __init__(
        self,
        *,
        command_managers: list,
        server_manager, 
        guild_settings_service,
        permission_service,
        dev_guild_id: int | None = None,
    ):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix="!",
            intents=intents,
        )

        self.server_manager = server_manager
        self.command_managers = command_managers
        self.guild_settings_service = guild_settings_service
        self.permission_service = permission_service
        self.dev_guild_id = dev_guild_id

    
        self.server_group = Group(
            name="server",
            description="Manage game servers",
        )
        self.create_group = Group(
            name="create",
            description="Create a new game server (instantly starts up)",
            parent=self.server_group,
        )
        self.edit_group = Group(
            name="edit",
            description="Edit attributes of game server",
            parent=self.server_group
        )

        for command_manager, group_name, game_name in self.command_managers:
            game_group = Group(
                name=group_name,
                description=f"{game_name} specific commands",
                parent=self.server_group,
            )

            command_manager.register_commands(
                game_group=game_group,
                create_group=self.create_group,
                edit_group=self.edit_group,
            )


    async def setup_hook(self):
        await self.load_extension("bot.commands.general")
        await self.load_extension("bot.commands.admin")
        await self.load_extension("bot.commands.server")
        await self.load_extension("bot.commands.server_backups")
        await self.load_extension("bot.commands.server_lifetime")

        self.tree.add_command(self.server_group)

        if self.dev_guild_id:
            guild = discord.Object(id=self.dev_guild_id)

            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

            print(
                f"[bot] Commands synced to development guild "
                f"{self.dev_guild_id}"
            )
        else:
            await self.tree.sync()

            print("[bot] Global commands synced.")

    async def on_ready(self):
        print(
            f"[bot] Logged in as {self.user} "
            f"(app_id={self.application_id})"
        )

        print(
            f"[bot] Connected guilds: "
            f"{[guild.id for guild in self.guilds]}"
        )