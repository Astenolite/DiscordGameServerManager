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
from games.minecraft.config.minecraft_config import MinecraftConfig


server_name = "TestServerMinecraft"
compose_directory_path = COMPOSE_FILES_DIRECTORY_PATH / MinecraftConfig.system_name  / server_name
compose_file = COMPOSE_FILES_DIRECTORY_PATH / MinecraftConfig.system_name / server_name / f"{server_name}.yml"
container_directory_path = GAME_SERVERS_DIRECTORY_PATH / MinecraftConfig.system_name / server_name

final_server_context = {
    "server_name": server_name,
    "compose_directory_path": str(compose_directory_path),
    "compose_file": str(compose_file),
    "container_directory_path": str(container_directory_path),
    "port": 25010,
    "server_type": "VANILLA",
    "version": "1.20.1",
    "java_version": "java17",
    "memory": 4,
    "max_players": 10,
    "online_mode": True,
    "difficulty": "normal",
    "render_distance": 16
}

@pytest.fixture
async def setup_directories():
    data_manager = DataManager()
    docker_manager = DockerManager()

    await data_manager.create_directory(COMPOSE_FILES_DIRECTORY_PATH / MinecraftConfig.system_name)
    await data_manager.create_directory(GAME_SERVERS_DIRECTORY_PATH / MinecraftConfig.system_name)
    await data_manager.create_directory(BACKUPS_DIRECTORY_PATH / MinecraftConfig.system_name)

    yield

    if await docker_manager.container_exists(server_name):
        await docker_manager.stop(server_name)
        await docker_manager.compose_down(compose_file)

    await data_manager.delete_directory(COMPOSE_FILES_DIRECTORY_PATH / MinecraftConfig.system_name)
    await data_manager.delete_directory(GAME_SERVERS_DIRECTORY_PATH / MinecraftConfig.system_name)
    await data_manager.delete_directory(BACKUPS_DIRECTORY_PATH / MinecraftConfig.system_name)

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

        if game_dict["name"] == MinecraftConfig.game_name:
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


async def test_ark_survival_ascended_lifecycle(server_managers):
    server_manager = server_managers.server_manager
    server_manager_extra = server_managers.server_manager_extra
    data_manager = DataManager()
    docker_manager = DockerManager()


    discord_context = {
        "server_name": server_name,
        "port": 25010,
        "server_type": "VANILLA",
        "version": "1.20.1",
        "memory": 4,
        "max_players": 10,
        "online_mode": True,
        "difficulty": "normal",
        "render_distance": 16
    }


    print(f"[{MinecraftConfig.game_name}] Testing server creation", flush=True)
    await server_manager_extra.create_server(discord_context)
    assert await data_manager.directory_exists(compose_directory_path) # check server directory exists
    assert await data_manager.file_exists(compose_file) # check compose file exists
    assert await data_manager.file_exists(compose_directory_path / "context.json") # check context file exists
    assert await data_manager.read_context_file(compose_directory_path) == final_server_context # check server context is correct
    assert await docker_manager.container_exists(server_name) # check container was created
    assert await docker_manager.container_isOnline(server_name) is False # check container is offline
    print(f"[{MinecraftConfig.game_name}] Server creation successful", flush=True)

    # Start server
    print(f"[{MinecraftConfig.game_name}] Testing server startup", flush=True)
    await server_manager.start_server(server_name)
    assert await docker_manager.container_isOnline(server_name) # check server turns on
    # TODO add check for server health
    print(f"[{MinecraftConfig.game_name}] Server startup successful", flush=True)


    # Stop server
    print(f"[{MinecraftConfig.game_name}] Testing server stoping", flush=True)
    await server_manager.stop_server(server_name)
    assert await docker_manager.container_isOnline(server_name) is False # check server turns off
    print(f"[{MinecraftConfig.game_name}] Server stoping successful", flush=True)

    print(f"[{MinecraftConfig.game_name}] Testing server backup", flush=True)
    for world_directory in MinecraftConfig.world_directories:
        await data_manager.create_directory(container_directory_path / world_directory)
    for i, world_directory in enumerate(MinecraftConfig.world_directories):
        await data_manager.create_context_file(container_directory_path / world_directory, {"file": i})

    await server_manager.backup_server(server_name)
    backups_list = await server_manager.list_backups(server_name)
    assert len(backups_list) == 1 # check only one backup exists
    for i, world_directory in enumerate(MinecraftConfig.world_directories):
        assert await data_manager.file_exists(BACKUPS_DIRECTORY_PATH / MinecraftConfig.system_name / server_name / backups_list[0] / world_directory / "context.json") # check files exist
        assert await data_manager.read_context_file(BACKUPS_DIRECTORY_PATH / MinecraftConfig.system_name / server_name / backups_list[0] / world_directory) == {"file": i} # check file contents are correct
    print(f"[{MinecraftConfig.game_name}] Server backup successful", flush=True)


    print(f"[{MinecraftConfig.game_name}] Testing server reset", flush=True)
    await server_manager.reset_server(server_name)
    for i, world_directory in enumerate(MinecraftConfig.world_directories):
        assert await data_manager.file_exists(container_directory_path / world_directory / "context.json") is False # check all previously created files dissapeared
    print(f"[{MinecraftConfig.game_name}] Server reset successful", flush=True)

    # Restore server
    print(f"[{MinecraftConfig.game_name}] Testing server restore", flush=True)
    await server_manager.restore_backup(server_name)
    for i, world_directory in enumerate(MinecraftConfig.world_directories):
        assert await data_manager.file_exists(container_directory_path / world_directory / "context.json") # check files exist
        assert await data_manager.read_context_file(container_directory_path / world_directory) == {"file": i} # check file contents are correct
    print(f"[{MinecraftConfig.game_name}] Server restore successful", flush=True)

    # Delete backup
    print(f"[{MinecraftConfig.game_name}] Testing backup deletion", flush=True)
    await server_manager.delete_backup(server_name, backups_list[0])
    assert await data_manager.directory_exists(BACKUPS_DIRECTORY_PATH / MinecraftConfig.system_name / server_name / backups_list[0]) is False # check directory doesn't exist anymore
    assert len(await server_manager.list_backups(server_name)) == 0 # check 0 backups are reported
    print(f"[{MinecraftConfig.game_name}] Backup deletion successful", flush=True)


    print(f"[{MinecraftConfig.game_name}] Testing server deletion", flush=True)
    await server_manager.delete_server(server_name)
    assert await docker_manager.container_exists(server_name) is False # check docker container no longer exists
    assert await data_manager.directory_exists(container_directory_path) is False # check container mounts were deleted
    assert await data_manager.directory_exists(compose_directory_path) is False # check compose directory was deleted
    print(f"[{MinecraftConfig.game_name}] Server deletion successful", flush=True)

