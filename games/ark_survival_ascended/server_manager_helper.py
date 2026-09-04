from pathlib import Path

from games.abstract.game_server_manager_helper import GameServerManagerHelper
from .config.ark_survival_ascended_config import ArkSurvivalAscendedConfig

class ServerManagerHelper(GameServerManagerHelper):
    config = ArkSurvivalAscendedConfig

    def get_server_cluster(self, server_name: str) -> str:
        compose_file = next(self.compose_directory.rglob(f"{server_name}.yml"), None)
        if not compose_file:
            raise FileNotFoundError(f"Server {server_name} does not exist")

        return compose_file.parents[1].name

    async def get_compose_directory(self, server_name: str) -> Path:
        return self.compose_directory / self.get_server_cluster(server_name) / server_name

    async def get_container_directory(self, server_name: str) -> Path:
        return self.containers_directory / self.get_server_cluster(server_name) / server_name

    async def get_backup_directory(self, server_name: str) -> Path:
        return self.backups_directory / self.get_server_cluster(server_name) / server_name



    

