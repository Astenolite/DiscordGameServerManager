import pytest

from pathlib import Path
from types import SimpleNamespace

TESTS_DIRECTORY_PATH = Path("/srv/GameServers/Tests/")
# from config import TESTS_DIRECTORY_PATH
COMPOSE_FILES_DIRECTORY_PATH = TESTS_DIRECTORY_PATH / "Compose" 
GAME_SERVERS_DIRECTORY_PATH = TESTS_DIRECTORY_PATH / "Servers" 
BACKUPS_DIRECTORY_PATH = TESTS_DIRECTORY_PATH / "Backups" 


from core.server_manager import ServerManager
from core.docker_manager import DockerManager
from core.data_manager import DataManager
from core.backup_manager import BackupManager
from core.server_registry import ServerRegistry
from core.compose_manager import ComposeManager
from games.registry import GAME_REGISTRY
from games.ark_survival_ascended.config.ark_survival_ascended_config import ArkSurvivalAscendedConfig

cluster_name = "testCluster"
cluster_id = 123456789
server_name = "TestServerArkSurvivalAscended"
compose_directory_path = COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / server_name
compose_file = COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / server_name / f"{server_name}.yml"
container_directory_path = GAME_SERVERS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / server_name
final_cluster_context = {"name": cluster_name, "id": cluster_id, "mods": []}
final_server_context = {
    "server_name": server_name,
    "compose_directory_path": compose_directory_path,
    "compose_file": compose_file,
    "container_directory_path": container_directory_path,
    "game_port": 25000,
    "steam_port": 25001,
    "map_name": "TheIsland",
    "max_players": 5,
    "cluster_id": cluster_id,
    "mods": [],
}

@pytest.fixture
async def setup_directories():
    data_manager = DataManager()
    docker_manager = DockerManager()

    await data_manager.create_directory(COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name)
    await data_manager.create_directory(GAME_SERVERS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name)
    await data_manager.create_directory(BACKUPS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name)

    yield

    if await docker_manager.container_exists(server_name):
        await docker_manager.stop(server_name)
        await docker_manager.compose_down(compose_file)

    await data_manager.delete_directory(COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name)
    await data_manager.delete_directory(GAME_SERVERS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name)
    await data_manager.delete_directory(BACKUPS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name)

@pytest.fixture
async def server_managers(setup_directories):
    docker_manager = DockerManager()
    data_manager = DataManager()
    compose_manager = ComposeManager("games/", data_manager)
    backup_manager = BackupManager(data_manager)
    server_registry = ServerRegistry(COMPOSE_FILES_DIRECTORY_PATH)

    server_manager_helpers = {}
    server_manager_extra = None
    for game_dict in GAME_REGISTRY:
        ServerManagerHelper = game_dict["server_manager_helper"]
        ServerManagerExtra = game_dict["server_manager_extra"]

        server_manager_helpers[game_dict["image"]] = ServerManagerHelper(
            compose_directory=COMPOSE_FILES_DIRECTORY_PATH,
            containers_directory=GAME_SERVERS_DIRECTORY_PATH,
            backups_directory=BACKUPS_DIRECTORY_PATH,
        )

        if game_dict["name"] == "ArkSurvivalAscended":
            server_manager_extra = ServerManagerExtra(
                docker_manager=docker_manager,
                compose_manager=compose_manager,
                data_manager=data_manager,
                server_registry=server_registry,
                compose_directory=COMPOSE_FILES_DIRECTORY_PATH,
                containers_directory=GAME_SERVERS_DIRECTORY_PATH,
                backups_directory=BACKUPS_DIRECTORY_PATH,
            )


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

    return SimpleNamespace(
        server_manager=server_manager,
        server_manager_extra=server_manager_extra,
    )


async def test_ark_survival_ascended_lifecycle(setup_directories, server_managers):
    server_manager = server_managers.server_manager
    server_manager_extra = server_managers.server_manager_extra
    data_manager = DataManager()
    docker_manager = DockerManager()


    discord_context = {
        "cluster_name": cluster_name,
        "server_name": server_name,
        "game_port": 25000,
        "steam_port": 25001,
        "map_name": "TheIsland",
        "max_players": 5,
    }

        

    # Create cluster
    await server_manager_extra.create_cluster(cluster_name, cluster_id)
    assert await data_manager.directory_exists(COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name) is True # check cluster directory exists
    assert await data_manager.file_exists(COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / "context.json") is True # check context file exists
    assert await data_manager.read_context_file(COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name) == final_cluster_context # check cluster context is correct


    # Create server
    await server_manager_extra.create_server(discord_context)
    assert await data_manager.directory_exists(compose_directory_path) is True # check server directory exists
    assert await data_manager.file_exists(compose_file) is True # check compose file exists
    assert await data_manager.file_exists(compose_directory_path / "context.json") is True # check context file exists
    assert await data_manager.read_context_file(compose_directory_path) == final_server_context # check server context is correct
    assert await docker_manager.container_exists(server_name) is True # check container was created
    assert await docker_manager.is_online(server_name) is False # check container is offline


    # Start server
    await server_manager.start_server(server_name)
    assert await docker_manager.is_online(server_name) is True # check server turns on
    # TODO add check for server health


    # Stop server
    await server_manager.stop_server(server_name)
    assert await docker_manager.is_online(server_name) is False # check server turns off


    for i, world_directory in enumerate(ArkSurvivalAscendedConfig.world_directories):
        await data_manager.create_context_file(container_directory_path / world_directory, {"file": i})

    # Backup server
    await server_manager.backup_server(server_name)
    backups_list = await server_manager.list_backups(server_name)
    assert len(backups_list) == 1 # check only one backup exists
    for i, world_directory in enumerate(ArkSurvivalAscendedConfig.world_directories):
        assert await data_manager.file_exists(BACKUPS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / server_name / backups_list[0] / world_directory / "context.json") is True # check files exist
        assert await data_manager.read_context_file(BACKUPS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / server_name / backups_list[0] / world_directory) == {"file": i} # check file contents are correct

    # Reset server
    await server_manager.reset_server(server_name)
    for i, world_directory in enumerate(ArkSurvivalAscendedConfig.world_directories):
        assert await data_manager.file_exists(container_directory_path / world_directory / "context.json") is False # check all previously created files dissapeared

    # Restore server
    await server_manager.restore_backup(server_name)
    for i, world_directory in enumerate(ArkSurvivalAscendedConfig.world_directories):
        assert await data_manager.file_exists(container_directory_path / world_directory / "context.json") is True # check files exist
        assert await data_manager.read_context_file(container_directory_path / world_directory) == {"file": i} # check file contents are correct

    # Delete backup
    await server_manager.delete_backup(server_name, backups_list[0])
    assert await data_manager.directory_exists(BACKUPS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name / server_name / backups_list[0]) is False # check directory doesn't exist anymore
    assert len(await server_manager.list_backups(server_name)) == 0 # check 0 backups are reported

    # Delete server
    await server_manager.delete_server(server_name)
    assert await docker_manager.container_exists(server_name) is False # check docker container no longer exists
    assert await data_manager.directory_exists(container_directory_path) is False # check container mounts were deleted
    assert await data_manager.directory_exists(compose_directory_path) is False # check compose directory was deleted

    # Delete cluster
    await server_manager_extra.delete_cluster(cluster_name)
    assert await data_manager.directory_exists(COMPOSE_FILES_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name) is False # check cluster compose directory was deleted
    assert await data_manager.directory_exists(GAME_SERVERS_DIRECTORY_PATH / ArkSurvivalAscendedConfig.system_name / cluster_name) is False # check cluster compose directory was deleted



