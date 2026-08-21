from pathlib import Path

from games.abstract.game_server_manager import GameServerManager

from .config.ark_survival_ascended_config import ArkSurvivalAscendedConfig
from .config.ark_survival_ascended_server_create_config import ArkSurvivalAscendedServerCreateConfig
from .config.ark_survival_ascended_server_edit_config import ArkSurvivalAscendedServerEditConfig

class ArkSurvivalAscendedServerManager(GameServerManager):

    config = ArkSurvivalAscendedConfig
    server_create_config = ArkSurvivalAscendedServerCreateConfig
    server_edit_config = ArkSurvivalAscendedServerEditConfig


    # throws error if a cluster with provided name does not exist
    async def cluster_existence_check(self, cluster_name: str) -> None:
        clusters = await self.get_clusters()
        print(clusters, flush=True)
        if cluster_name not in [cluster["name"] for cluster in clusters]:
            raise ValueError(f"Cluster {cluster_name} does not exist.")

    # throws error if a cluster with same name or id already exists
    async def cluster_nonexistence_check(self, cluster_name: str, cluster_id: str) -> None:
        clusters = await self.get_clusters()
        if cluster_name in [cluster["name"] for cluster in clusters]:
            raise ValueError(f"Cluster with name {cluster_name} already exists.")
        if cluster_id in [cluster["id"] for cluster in clusters]:
            raise ValueError(f"Cluster with id {cluster_id} already exists.")

    # throws error if cluster contains servers
    async def cluster_empty_check(self, cluster_name: str) -> None:
        if len(self.get_servers(cluster_name)) != 0:
            raise ValueError(f"Cluster {cluster_name} contains servers.")

    # throws error if not all servers in cluster are offline
    async def cluster_offline_check(self, cluster_name: str) -> None:
        servers = self.get_servers(cluster_name)
        online_servers = []
        for server in servers:
            if await self.server_manager.docker_manager.is_online(server):
                online_servers.append(server)

        if len(online_servers) > 0:
            raise ValueError(f"Servers {online_servers} need to be offline")

    # throws error if mod is in cluster
    async def mod_nonexistence_check(self, cluster_name: str, mod_id: int) -> None:
        cluster_compose_directory = self.get_cluster_compose_directory(cluster_name)
        existing_mods = (await self.server_manager.data_manager.read_context_file(cluster_compose_directory))["mods"]
        mod_ids = [mod_id for mod_id, _, _ in existing_mods]
        if mod_id in mod_ids:
            raise ValueError(f"Mod {mod_id} is already in this cluster.")

    # throws error if mod is not in cluster
    async def mod_existence_check(self, cluster_name: str, mod_id: int) -> None:
        cluster_compose_directory = self.get_cluster_compose_directory(cluster_name)
        existing_mods = (await self.server_manager.data_manager.read_context_file(cluster_compose_directory))["mods"]
        mod_ids = [mod_id for mod_id, _, _ in existing_mods]
        if mod_id not in mod_ids:
            raise ValueError(f"Mod {mod_id} is not in this cluster.")



    def get_cluster_compose_directory(self, cluster_name: str) -> Path:
        return (self.compose_directory / Path(cluster_name))

    def get_cluster_container_directory(self, cluster_name: str) -> Path:
        return (self.containers_directory / Path(cluster_name))

    def get_cluster_backup_directory(self, cluster_name: str) -> Path:
        return (self.backups_directory / Path(cluster_name))
    
    def get_server_compose_directory(self, cluster_name: str, server_name: str) -> Path:
        return self.compose_directory / cluster_name / server_name

    def get_server_compose_file(self, cluster_name: str, server_name: str) -> Path:
        return self.get_server_compose_directory(cluster_name, server_name) / f"{server_name}.yml"
    
    def get_server_container_directory(self, cluster_name: str, server_name: str) -> Path:
        return self.containers_directory / cluster_name / server_name

    def get_server_backup_directory(self, cluster_name: str, server_name: str) -> Path:
        return self.backups_directory / cluster_name / server_name

    def get_server_cluster(self, server_name: str) -> str:
        compose_file = next(self.compose_directory.rglob(f"{server_name}.yml"), None)
        if not compose_file:
            raise FileNotFoundError(f"Server {server_name} does not exist")

        return compose_file.parents[1].name



    async def create_cluster(self, cluster_name: str, cluster_id: int):
        await self.cluster_nonexistence_check(
            cluster_name=cluster_name, 
            cluster_id=cluster_id,
        )

        cluster_compose_directory = self.get_cluster_compose_directory(cluster_name)
        context = {
            "name": cluster_name,
            "id": cluster_id,
            "mods": []
        }

        await self.server_manager.data_manager.create_directory(cluster_compose_directory)
        await self.server_manager.data_manager.create_context_file(cluster_compose_directory, context)


    async def delete_cluster(self, cluster_name: str):
        await self.cluster_existence_check(cluster_name)
        await self.cluster_empty_check(cluster_name)

        cluster_compose_directory = self.get_cluster_compose_directory(cluster_name)
        cluster_container_directory = self.get_cluster_container_directory(cluster_name)

        await self.server_manager.data_manager.delete_directory(cluster_compose_directory)
        await self.server_manager.data_manager.delete_directory(cluster_container_directory)


    async def add_mod(self, cluster_name: str, mod_id: int, mod_name: str, mod_type: str):
        await self.cluster_existence_check(cluster_name)
        await self.cluster_offline_check(cluster_name)
        await self.mod_nonexistence_check(cluster_name, mod_id)

        # add mod to cluster context
        context = await self.server_manager.data_manager.read_context_file(self.get_cluster_compose_directory(cluster_name))
        context["mods"].append((mod_id, mod_name, mod_type))
        mod_ids = [mod_id for mod_id, _, _ in context["mods"]]
        await self.server_manager.data_manager.edit_context_file(self.get_cluster_compose_directory(cluster_name), context)

        # edit all servers in cluster 
        for server_name in self.get_servers(cluster_name):
            context = {
                "game_port": None,
                "steam_port": None,
                "max_players": None,
                "server_name": server_name,
                "mods": ",".join(map(str, mod_ids)),
                "compose_directory_path": str(self.get_server_compose_directory(cluster_name, server_name)),
                "compose_file": str(self.get_server_compose_file(cluster_name, server_name)),
            }

            await super().edit_server(context)


    async def remove_mod(self, cluster_name: str, mod_id: int):
        await self.cluster_existence_check(cluster_name)
        await self.cluster_offline_check(cluster_name)
        await self.mod_existence_check(cluster_name, mod_id)

        # remove mod from cluster context
        context = await self.server_manager.data_manager.read_context_file(self.get_cluster_compose_directory(cluster_name))
        context["mods"] = [mod for mod in context["mods"] if mod[0] != mod_id]
        mod_ids = [id for id, _, _ in context["mods"] if id != mod_id ]
        await self.server_manager.data_manager.edit_context_file(self.get_cluster_compose_directory(cluster_name), context)

        # edit all servers in cluster 
        for server_name in self.get_servers(cluster_name):
            context = {
                "game_port": None,
                "steam_port": None,
                "max_players": None,
                "server_name": server_name,
                "mods": ",".join(map(str, mod_ids)),
                "compose_directory_path": str(self.get_server_compose_directory(cluster_name, server_name)),
                "compose_file": str(self.get_server_compose_file(cluster_name, server_name)),
            }

            await super().edit_server(context)

    async def list_mods(self, cluster_name: str) -> list:
        await self.cluster_existence_check(cluster_name)

        return (await self.server_manager.data_manager.read_context_file(self.get_cluster_compose_directory(cluster_name)))["mods"]


    async def create_server(self, context: dict):
        await self.cluster_existence_check(context["cluster_name"])

    
        cluster = await self.get_cluster(context["cluster_name"])
        cluster_name = cluster["name"]
        cluster_id = cluster["id"]
        cluster_mod_ids = [id for id, _, _ in cluster["mods"]]
        server_name = context["server_name"]    
        
        context["container_directory_path"] = str(self.get_server_container_directory(cluster_name, server_name))
        context["compose_directory_path"] = str(self.get_server_compose_directory(cluster_name, server_name))
        context["compose_file"] = str(self.get_server_compose_file(cluster_name, server_name))
        context["cluster_directory_path"] = str(self.get_cluster_container_directory(cluster_name) / "cluster")
        context["cluster_id"] = cluster_id
        context["mods"] = ",".join(map(str, cluster_mod_ids))

        await super().create_server(context)
        
        
    async def delete_server(self, server_name: str):
        await self.server_type_check(server_name)

        cluster_name = self.get_server_cluster(server_name)
        context = {
            "server_name": server_name,
            "container_directory_path": str(self.get_server_container_directory(cluster_name, server_name)),
            "compose_directory_path": str(self.get_server_compose_directory(cluster_name, server_name)),
            "compose_file": str(self.get_server_compose_file(cluster_name, server_name))
        }

        await self.server_manager.delete_server(context)


    async def edit_server(self, context: dict):
        await self.server_type_check(context["server_name"])

        server_name = context["server_name"]
        cluster_name = self.get_server_cluster(server_name)

        context["compose_directory_path"] = str(self.get_server_compose_directory(cluster_name, server_name))
        context["compose_file"] = str(self.get_server_compose_file(cluster_name, server_name))

        await super().edit_server(context)


    async def reset_server(self, server_name: str):
        await self.server_type_check(server_name)

        cluster_name = self.get_server_cluster(server_name)
        await super().reset_server(
            server_name=server_name,
            server_container_directory=self.get_server_container_directory(cluster_name, server_name)
        )


    async def backup_server(self, server_name: str):
        await self.server_type_check(server_name)

        cluster_name = self.get_server_cluster(server_name)

        await super().backup_server(
            server_name=server_name,
            server_container_directory=self.get_server_container_directory(cluster_name, server_name),
            server_backup_directory=self.get_server_backup_directory(cluster_name, server_name),
        )


    async def restore_server(self, server_name: str, backup_name: str):
        await self.server_type_check(server_name)

        cluster_name = self.get_server_cluster(server_name)

        await super().restore_server(
            server_name=server_name,
            backup_name=backup_name,
            server_container_directory=str(self.get_server_container_directory(cluster_name, server_name)),
            server_backup_directory=str(self.get_server_backup_directory(cluster_name, server_name))
        )

 
    async def list_backups(self, server_name: str):
        await self.server_type_check(server_name)

        cluster_name = self.get_server_cluster(server_name)

        return self.server_manager.backup_manager.get_backups(self.get_server_backup_directory(cluster_name, server_name))


    async def delete_backup(self, server_name: str, backup_name: str):
        await self.server_type_check(server_name)
        
        cluster_name = self.get_server_cluster(server_name)

        await super().delete_backup(
            server_name=server_name,
            backup_directory_path=str(self.get_server_backup_directory(cluster_name, server_name)),
            backup_name=backup_name
        )
    

    
    
    # Returns a list of names of all servers in cluster
    def get_servers(self, cluster_name) -> list[str]:
        servers = []

        for server_directory in self.get_cluster_compose_directory(cluster_name).iterdir():
            if server_directory.is_dir():
                servers.append(server_directory.name)

        return servers

    # Returns a list configs of all clusters
    async def get_clusters(self) -> list[dict]:
        clusters = []
        for cluster_directory in self.compose_directory.iterdir():
            if cluster_directory.is_dir():
                cluster = await self.server_manager.data_manager.read_context_file(cluster_directory)
                clusters.append(cluster)

        return clusters

    # Returns the config of the cluster
    async def get_cluster(self, cluster_name) -> dict:
        cluster_directory = self.get_cluster_compose_directory(cluster_name)
        return await self.server_manager.data_manager.read_context_file(cluster_directory)
    

