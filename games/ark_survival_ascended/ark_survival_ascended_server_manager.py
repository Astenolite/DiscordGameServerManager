from pathlib import Path

from games.abstract.game_server_manager import GameServerManager
from core.server_manager import ServerManager

from .config.ark_survival_ascended_config import ArkSurvivalAscendedConfig
from .config.ark_survival_ascended_server_create_config import ArkSurvivalAscendedServerCreateConfig
from .config.ark_survival_ascended_server_edit_config import ArkSurvivalAscendedServerEditConfig

class ArkSurvivalAscendedServerManager(GameServerManager):

    config = ArkSurvivalAscendedConfig
    server_create_config = ArkSurvivalAscendedServerCreateConfig
    server_edit_config = ArkSurvivalAscendedServerEditConfig

    def __init__(
        self, 
        server_manager: ServerManager,
    ):
        self.server_manager = server_manager

        self.ark_survival_ascended_compose_directory = (server_manager.compose_directory / Path(self.config.system_name))
        self.ark_survival_ascended_servers_directory = (server_manager.servers_directory / Path(self.config.system_name))
        self.ark_survival_ascended_backups_directory = (server_manager.backups_directory / Path(self.config.system_name))

    async def setup(self):
        await self.server_manager.data_manager.create_directory(self.ark_survival_ascended_compose_directory)
        await self.server_manager.data_manager.create_directory(self.ark_survival_ascended_servers_directory)
        await self.server_manager.data_manager.create_directory(self.ark_survival_ascended_backups_directory)


    async def create_cluster(self, cluster_name: str, cluster_id: int):
        clusters = await self.get_clusters_context()

        for cluster in clusters:
            if cluster["name"] == cluster_name:  
                raise ValueError(f"Cluster {cluster_name} already exists")
            if cluster["id"] == cluster_id:
                raise ValueError(f"Cluster with id {cluster_id} already exists")


        cluster_compose_directory = self.ark_survival_ascended_compose_directory / cluster_name
        context = {
            "name": cluster_name,
            "id": cluster_id,
            "mods": []
        }

        await self.server_manager.data_manager.create_directory(cluster_compose_directory)
        await self.server_manager.data_manager.create_context_file(cluster_compose_directory, context)

    async def delete_cluster(self, cluster_name: str):
        if cluster_name not in self.get_clusters():
            raise ValueError(f"Cluster {cluster_name} does not exist")

        if len(self.get_servers(cluster_name)) != 0:
            raise ValueError(f"Cluster {cluster_name} contains servers.")

        await self.server_manager.data_manager.delete_directory(self.get_cluster_compose_directory(cluster_name))
        await self.server_manager.data_manager.delete_directory(self.get_cluster_server_directory(cluster_name))

    async def add_mod(self, cluster_name: str, mod_id: int, mod_name: str, mod_type: str):

        # check cluster exists
        if cluster_name not in self.get_clusters():
            raise ValueError(f"Cluster {cluster_name} does not exist")

        # check all servers are offline
        for server in self.get_servers(cluster_name):
            await self.server_manager.offline_check(server)

        # check for mod existence
        context = await self.server_manager.data_manager.read_context_file(self.get_cluster_compose_directory(cluster_name))
        existing_mods = context["mods"]
        mod_ids = [mod_id for mod_id, _, _ in existing_mods]
        if mod_id in mod_ids:
            raise ValueError(f"Mod {mod_id} is already in this cluster")

        # add mod to cluster context
        context["mods"].append((mod_id, mod_name, mod_type))
        mod_ids.append(mod_id)
        await self.server_manager.data_manager.edit_context_file(self.get_cluster_compose_directory(cluster_name), context)

        # edit all servers in cluster 
        for server_name in self.get_servers(cluster_name):
            cluster_name = self.get_cluster(server_name)
            
            compose_directory_path = (
                self.ark_survival_ascended_compose_directory /
                cluster_name / 
                server_name
            )
            compose_file = (
                compose_directory_path /
                f"{server_name}.yml"
            )
            complete_context = {
                "game_port": None,
                "steam_port": None,
                "max_players": None,
                "server_name": server_name,
                "mods": ",".join(map(str, mod_ids)),
                "compose_directory_path": str(compose_directory_path),
                "compose_file": str(compose_file)
            }

            try:
                config = self.server_edit_config(**complete_context)
                await self.server_manager.edit_server(config.model_dump(exclude_none=True), self.config.compose_template)
            except Exception as e:
                raise ValueError("Invalid server parameters") from e

    async def remove_mod(self, cluster_name: str, mod_id: int):
        # check cluster exists
        if cluster_name not in self.get_clusters():
            raise ValueError(f"Cluster {cluster_name} does not exist")

        # check all servers are offline
        for server in self.get_servers(cluster_name):
            await self.server_manager.offline_check(server)

        context = await self.server_manager.data_manager.read_context_file(self.get_cluster_compose_directory(cluster_name))
        existing_mods = context["mods"]
        mod_ids = [mod_id for mod_id, _, _ in existing_mods]
        if mod_id not in mod_ids:
            raise ValueError(f"Mod {mod_id} is not in this cluster")

        # remove mod from cluster context
        context["mods"] = [mod for mod in context["mods"] if mod[0] != mod_id]
        mod_ids = [mod for mod in mod_ids if mod == mod_id]
        await self.server_manager.data_manager.edit_context_file(self.get_cluster_compose_directory(cluster_name), context)

        # edit all cluster composes
        for server_name in self.get_servers(cluster_name):
            cluster_name = self.get_cluster(server_name)
            
            compose_directory_path = (
                self.ark_survival_ascended_compose_directory /
                cluster_name / 
                server_name
            )
            compose_file = (
                compose_directory_path /
                f"{server_name}.yml"
            )
            complete_context = {
                "game_port": None,
                "steam_port": None,
                "max_players": None,
                "server_name": server_name,
                "mods": ",".join(map(str, mod_ids)),
                "compose_directory_path": str(compose_directory_path),
                "compose_file": str(compose_file)
            }

            try:
                config = self.server_edit_config(**complete_context)
                await self.server_manager.edit_server(config.model_dump(exclude_none=True), self.config.compose_template)
            except Exception as e:
                raise ValueError("Invalid server parameters") from e

    async def list_mods(self, cluster_name: str) -> list:
        # check cluster exists
        if cluster_name not in self.get_clusters():
            raise ValueError(f"Cluster {cluster_name} does not exist")

        return (await self.server_manager.data_manager.read_context_file(self.get_cluster_compose_directory(cluster_name)))["mods"]

    async def create_server(self, discord_context: dict):
        
        if discord_context["cluster_name"] not in self.get_clusters():
            raise ValueError(f"Cluster {discord_context["cluster_name"]} does not exist")

        cluster_context = next((context for context in (await self.get_clusters_context()) if context.get("name") == discord_context["cluster_name"]), None)
        cluster_name = cluster_context["name"]
        cluster_id = cluster_context["id"]
        mods = cluster_context["mods"]
        server_name = discord_context["server_name"]

        
        server_directory_path = (
            self.ark_survival_ascended_servers_directory /
            cluster_name / 
            server_name
        )
        compose_directory_path = (
            self.ark_survival_ascended_compose_directory /
            cluster_name / 
            server_name
        )
        compose_file = (
            compose_directory_path /
            f"{server_name}.yml"
        )

        complete_context = {
            **discord_context,
            "server_directory_path": str(server_directory_path),
            "compose_directory_path": str(compose_directory_path),
            "compose_file": str(compose_file),
            "cluster_directory_path": str(self.get_cluster_server_directory(cluster_name) / "cluster"),
            "cluster_id": cluster_id,
            "mods": ",".join(map(str, mods))
        }

        try:
            config = self.server_create_config(**complete_context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e

        await self.server_manager.create_server(config.model_dump(), self.config.compose_template)
        
    async def delete_server(self, server_name: str):
        server_directory_path = self.get_server_directory(server_name)
        compose_directory_path = self.get_compose_directory(server_name)
        compose_file = compose_directory_path / f"{server_name}.yml"

        complete_contetx = {
            "server_name": server_name,
            "server_directory_path": str(server_directory_path),
            "compose_directory_path": str(compose_directory_path),
            "compose_file": str(compose_file)
        }

        await self.server_manager.delete_server(complete_contetx)

    async def edit_server(self, discord_context: dict):
        if discord_context["server_name"] not in self.get_server_list():
            raise ValueError(f"{discord_context["server_name"]} is not a {self.config.game_name} server or doesn't extist.")

        server_name = discord_context["server_name"]
        cluster_name = self.get_cluster(server_name)

        compose_directory_path = (
            self.ark_survival_ascended_compose_directory /
            cluster_name / 
            server_name
        )
        compose_file = (
            compose_directory_path /
            f"{server_name}.yml"
        )

        complete_context = {
            **discord_context,
            "compose_directory_path": str(compose_directory_path),
            "compose_file": str(compose_file)
        }
        try:
            config = self.server_edit_config(**complete_context)
        except Exception as e:
            raise ValueError("Invalid server parameters") from e

        await self.server_manager.edit_server(config.model_dump(exclude_none=True), self.config.compose_template)

    async def reset_server(self, server_name: str):
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a {self.config.game_name} server or doesn't extist.")

        server_directory = self.get_server_directory(server_name)
        complete_context = {
            "server_name": server_name,
            "server_data_directory_paths": []
        }
        for world_directory in self.config.world_directories:
            complete_context["server_data_directory_paths"].append((
                server_directory /
                world_directory
            ))

        await self.server_manager.reset_server(complete_context)

    async def backup_server(self, server_name: str):
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a {self.config.game_name} server or doesn't extist.")

        server_directory = self.get_server_directory(server_name)
        backup_directory = self.get_backup_directory(server_name)

        complete_context = {
            "server_name": server_name,
            "active_data": self.config.world_directories,
            "backup_directory_path": backup_directory,
            "active_directory_path": server_directory,
        }

        await self.server_manager.backup_server(complete_context)

        backups_list = await self.list_backups(server_name)
        while len(backups_list) > self.config.backup_no:
            await self.delete_backup(server_name, min(backups_list))
            backups_list.remove(min(backups_list))

    async def restore_server(self, server_name: str, backup_name: str):
        if server_name not in self.get_server_list():
            raise ValueError(f"{server_name} is not a {self.config.game_name} server or doesn't extist.")

        server_directory = self.get_server_directory(server_name)
        backup_directory = self.get_backup_directory(server_name)
        complete_context = {
            "server_name": server_name,
            "backup_name": backup_name,
            "active_directory_path": server_directory,
            "backup_directory_path": backup_directory,
        }

        await self.server_manager.restore_server(complete_context)

    async def list_backups(self, server_name: str):
        return self.get_backups(server_name)

    async def delete_backup(self, server_name: str, backup_name: str):

        backup_directory = self.get_backup_directory(server_name)

        if backup_name == "all":
            for backup in await self.list_backups(server_name):
                complete_context = {
                    "server_name": server_name,
                    "backup_name": backup,
                    "backup_directory_path": backup_directory
                }
                await self.server_manager.delete_backup(complete_context)
        else:
            complete_context = {
                "server_name": server_name,
                "backup_name": backup_name,
                "backup_directory_path": backup_directory
            }
            await self.server_manager.delete_backup(complete_context)



    def get_server_list(self) -> list[str]:
        servers = []

        for game_directory in Path(self.ark_survival_ascended_compose_directory).iterdir():
            if not game_directory.is_dir():
                continue

            for compose_file in game_directory.rglob("*.yml"):
                servers.append(compose_file.stem)
        
        return servers

    async def get_clusters_context(self) -> list[dict]:
        clusters = []

        for cluster_directory in self.ark_survival_ascended_compose_directory.iterdir():
            if cluster_directory.is_dir():
                cluster = await self.server_manager.data_manager.read_context_file(cluster_directory)
                clusters.append(cluster)

        return clusters

    

    def get_cluster_compose_directory(self, cluster_name: str) -> Path:
        return (self.ark_survival_ascended_compose_directory / Path(cluster_name))

    def get_compose_directory(self, server_name: str) -> Path:
        return self.get_cluster_compose_directory(self.get_cluster(server_name)) / server_name

    def get_cluster_server_directory(self, cluster_name: str) -> Path:
        return (self.ark_survival_ascended_servers_directory / Path(cluster_name))

    def get_server_directory(self, server_name: str) -> Path:
        return self.get_cluster_server_directory(self.get_cluster(server_name)) / server_name

    def get_cluster_backup_directory(self, cluster_name: str) -> Path:
        return (self.ark_survival_ascended_backups_directory / Path(cluster_name))

    def get_backup_directory(self, server_name: str) -> Path:
            return self.get_cluster_backup_directory(self.get_cluster(server_name)) / server_name

    def get_cluster(self, server_name: str) -> str:
        compose_file = next(self.ark_survival_ascended_compose_directory.rglob(f"{server_name}.yml"), None)
        if not compose_file:
            raise FileNotFoundError(f"Server {server_name} does not exist")

        return compose_file.parents[1].name

    def get_servers(self, cluster_name) -> list[str]:
        servers = []

        for server_directory in self.get_cluster_compose_directory(cluster_name).iterdir():
            if server_directory.is_dir():
                servers.append(server_directory.name)

        return servers

    def get_clusters(self) -> list[str]:
        clusters = []

        for cluster_directory in self.ark_survival_ascended_compose_directory.iterdir():
            if cluster_directory.is_dir():
                clusters.append(cluster_directory.name)

        return clusters

    def get_backups(self, server_name: str) -> list[str]:
        return self.server_manager.backup_manager.get_backups(self.get_backup_directory(server_name))

