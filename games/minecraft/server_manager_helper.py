from games.abstract.game_server_manager_helper import GameServerManagerHelper
from .config.minecraft_config import MinecraftConfig

class ServerManagerHelper(GameServerManagerHelper):
    config = MinecraftConfig
    ...