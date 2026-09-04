from pathlib import Path

from games.abstract.game_server_manager import GameServerManager

from .config.minecraft_config import MinecraftConfig
from .config.minecraft_server_create_config import MinecraftServerCreateConfig
from .config.minecraft_server_edit_config import MinecraftServerEditConfig

class MinecraftServerManager(GameServerManager):

    config = MinecraftConfig
    server_create_config = MinecraftServerCreateConfig
    server_edit_config = MinecraftServerEditConfig



    def get_java_version(self, minecraft_version: str) -> str:
        if minecraft_version is None:
            return None

        for java in self.config.java_versions:
            if java["min_minecraft"] <= minecraft_version and minecraft_version <= java["max_minecraft"]:
                print(java, flush=True)
                return java["container_java"]
    

    async def create_server(self, context: dict):
        context["java_version"] = self.get_java_version(context["version"])
        context["container_directory_path"] = str(self.get_container_directory(context["server_name"]))
        context["compose_directory_path"] = str(self.get_compose_directory(context["server_name"]))
        context["compose_file"] = str(self.get_compose_file(context["server_name"]))

        await super().create_server(context)

        

    async def edit_server(self, context: dict):
        await self.server_type_check(context["server_name"])

        context["java_version"] = self.get_java_version(context["version"])
        context["compose_directory_path"] = str(self.get_compose_directory(context["server_name"]))
        context["compose_file"] = str(self.get_compose_directory(context["server_name"]))

        await super().edit_server(context)



    async def make_op(self, server_name: str, account: str):
        await self.server_type_check(server_name)

        command = [
            "rcon-cli", 
            "op", 
            account
        ]
        await self.docker_manager.execute_command(server_name, command)

    async def remove_op(self, server_name: str, account: str):
        await self.server_type_check(server_name)

        command = [
            "rcon-cli", 
            "deop", 
            account
        ]

        await self.docker_manager.execute_command(server_name, command)