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

        
    async def delete_server(self, server_name: str):
        await self.server_type_check(server_name)

        context = {
            "server_name": server_name,
            "container_directory_path": str(self.get_container_directory(server_name)),
            "compose_directory_path": str(self.get_compose_directory(server_name)),
            "compose_file": str(self.get_compose_file(server_name))
        }

        await self.server_manager.delete_server(context)


    async def edit_server(self, context: dict):
        await self.server_type_check(context["server_name"])

        context["compose_directory_path"] = str(self.get_compose_directory(context["server_name"]))
        context["compose_file"] = str(self.get_compose_directory(context["server_name"]))

        await super().edit_server(context)


    async def reset_server(self, server_name: str):
        await self.server_type_check(server_name)
        
        await super().reset_server(
            server_name=server_name,
            server_container_directory=self.get_container_directory(server_name)
        )


    async def backup_server(self, server_name: str):
        await self.server_type_check(server_name)

        await super().backup_server(
            server_name=server_name,
            server_container_directory=self.get_container_directory(server_name),
            server_backup_directory=self.get_backup_directory(server_name),
        )


    async def restore_server(self, server_name: str, backup_name: str):
        await self.server_type_check(server_name)

        await super().restore_server(
            server_name=server_name,
            backup_name=backup_name,
            server_container_directory=str(self.get_container_directory(server_name)),
            server_backup_directory=str(self.get_backup_directory(server_name))
        )


    async def list_backups(self, server_name: str):
        await self.server_type_check(server_name)

        return self.server_manager.backup_manager.get_backups(self.get_backup_directory(server_name))


    async def delete_backup(self, server_name: str, backup_name: str):
        await self.server_type_check(server_name)

        await super().delete_backup(
            server_name=server_name,
            backup_directory_path=str(self.get_backup_directory(server_name)),
            backup_name=backup_name,
        )