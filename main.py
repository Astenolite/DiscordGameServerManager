import asyncio

from pathlib import Path
from config import DISCORD_TOKEN, DEV_GUILD_ID, COMPOSE_FILES_DIRECTORY_PATH, GAME_SERVERS_DIRECTORY_PATH, BACKUPS_DIRECTORY_PATH


from bot.client import GameServerManagerBot
from games.registry import GAME_REGISTRY


from core.docker_manager import DockerManager
from core.data_manager import DataManager
from core.compose_manager import ComposeManager
from core.server_registry import ServerRegistry
from core.backup_manager import BackupManager
from core.server_manager import ServerManager
# from core.game_registry import GameRegistry

# from database.database import Database
# from database.repositories.guild_repository import GuildRepository
# from database.repositories.server_repository import ServerRepository

# from services.permission_service import PermissionService
# from services.guild_settings_service import GuildSettingsService


async def main():
    print("[main] Starting", flush=True)

    docker_manager = DockerManager()
    print("[main] DockerManager created", flush=True)

    data_manager = DataManager()
    print("[main] DataManager created", flush=True)

    compose_manager = ComposeManager("games/", data_manager)
    print("[main] ComposeManager created", flush=True)

    backup_manager = BackupManager(data_manager)
    print("[main] BackupManager created", flush=True)

    server_registry = ServerRegistry(COMPOSE_FILES_DIRECTORY_PATH)

    server_manager_helpers = {}
    server_manager_extras = []
    command_managers = []
    for game_dict in GAME_REGISTRY:
        ServerManagerHelper = game_dict["server_manager_helper"]
        ServerManagerExtra = game_dict["server_manager_extra"]
        CommandManager = game_dict["command_manager"]

        server_manager_helpers[game_dict["image"]] = ServerManagerHelper(
            compose_directory=COMPOSE_FILES_DIRECTORY_PATH,
            containers_directory=GAME_SERVERS_DIRECTORY_PATH,
            backups_directory=BACKUPS_DIRECTORY_PATH,
        )

        serverManagerExtra = ServerManagerExtra(
            docker_manager=docker_manager,
            compose_manager=compose_manager,
            data_manager=data_manager,
            server_registry=server_registry,
            compose_directory=COMPOSE_FILES_DIRECTORY_PATH,
            containers_directory=GAME_SERVERS_DIRECTORY_PATH,
            backups_directory=BACKUPS_DIRECTORY_PATH,
        )

        commandManager = CommandManager(serverManagerExtra)
        command_managers.append((commandManager, serverManagerExtra.config.group_name, serverManagerExtra.config.game_name))



    server_manager = ServerManager(
        compose_manager=compose_manager,
        docker_manager=docker_manager,
        data_manager=data_manager,
        server_registry=server_registry,
        backup_manager=backup_manager,
        game_manager_helpers=server_manager_helpers,
        compose_directory=Path(COMPOSE_FILES_DIRECTORY_PATH),
        servers_directory=Path(GAME_SERVERS_DIRECTORY_PATH),
        backups_directory=Path(BACKUPS_DIRECTORY_PATH),
    )
    print("[main] ServerManager created", flush=True)

    print("[main] Creating bot", flush=True)

    bot = GameServerManagerBot(
        guild_settings_service=None,
        permission_service=None,
        dev_guild_id=DEV_GUILD_ID,
        command_managers=command_managers,
        server_manager=server_manager,
    )

    print("[main] Starting bot", flush=True)

    async with bot:
        print("[main] Logging into Discord", flush=True)

        await bot.login(DISCORD_TOKEN)

        print("[main] Discord login completed", flush=True)
        print("[main] Connecting gateway", flush=True)

        await bot.connect()


if __name__ == "__main__":
    asyncio.run(main())