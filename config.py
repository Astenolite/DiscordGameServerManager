import os
from pathlib import Path

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

DEV_GUILD_ID = int(os.environ.get("DEV_GUILD_ID")) if os.environ.get("DEV_GUILD_ID") else None

COMPOSE_FILES_DIRECTORY_PATH = Path(os.environ["COMPOSE_FILES_DIRECTORY_PATH"])
GAME_SERVERS_DIRECTORY_PATH = Path(os.environ["GAME_SERVERS_DIRECTORY_PATH"])
BACKUPS_DIRECTORY_PATH = Path(os.environ["BACKUPS_DIRECTORY_PATH"])
TESTS_DIRECTORY_PATH = Path(os.environ["TESTS_DIRECTORY_PATH"])

