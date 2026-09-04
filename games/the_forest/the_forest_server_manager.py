from pathlib import Path

from games.abstract.game_server_manager import GameServerManager

from .config.the_forest_config import TheForestConfig
from .config.the_forest_server_create_config import TheForestServerCreateConfig
from .config.the_forest_server_edit_config import TheForestServerEditConfig 

class TheForestServerManager(GameServerManager):

    config = TheForestConfig
    server_create_config = TheForestServerCreateConfig
    server_edit_config = TheForestServerEditConfig

    def get_compose_directory(self, server_name: str) -> Path:
            return self.compose_directory / server_name
    
    def get_compose_file(self, server_name: str) -> Path:
        return self.get_compose_directory(server_name) / f"{server_name}.yml"

    def get_container_directory(self, server_name: str) -> Path:
        return self.containers_directory / server_name

    def get_backup_directory(self, server_name: str) -> Path:
        return self.backups_directory / server_name

    

    async def create_server(self, context: dict):
        context["container_directory_path"] = str(self.get_container_directory(context["server_name"]))
        context["compose_directory_path"] = str(self.get_compose_directory(context["server_name"]))
        context["compose_file"] = str(self.get_compose_file(context["server_name"]))

        await super().create_server(context)


    async def edit_server(self, context: dict):
        await self.server_type_check(context["server_name"])

        context["compose_directory_path"] = str(self.get_compose_directory(context["server_name"]))
        context["compose_file"] = str(self.get_compose_directory(context["server_name"]))

        await super().edit_server(context)
