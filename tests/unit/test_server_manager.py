import pytest



from unittest.mock import create_autospec
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from types import SimpleNamespace

from core.server_manager import ServerManager
from core.docker_manager import DockerManager
from core.data_manager import DataManager
from core.backup_manager import BackupManager
from core.server_registry import ServerRegistry
from games.registry import GAME_REGISTRY

COMPOSE_FILES_DIRECTORY_PATH=Path("/srv/GameServers/Compose/")
GAME_SERVERS_DIRECTORY_PATH=Path("/srv/GameServers/Servers/")
BACKUPS_DIRECTORY_PATH=Path("/srv/GameServers/Backups/")


@pytest.fixture
def docker_manager():
    return create_autospec(DockerManager, instance=True)

@pytest.fixture
def data_manager():
    return create_autospec(DataManager, instance=True)

@pytest.fixture
def backup_manager():
    return create_autospec(BackupManager, instance=True)

@pytest.fixture
def server_registry():
    return create_autospec(ServerRegistry, instance=True)

@pytest.fixture
def server_manager(
    docker_manager,
    data_manager,
    backup_manager,
    server_registry,
):
    server_manager_helpers = {}
    for game_dict in GAME_REGISTRY:
        ServerManagerHelper = game_dict["server_manager_helper"]
        server_manager_helpers[game_dict["image"]] = ServerManagerHelper(
            compose_directory=COMPOSE_FILES_DIRECTORY_PATH,
            containers_directory=GAME_SERVERS_DIRECTORY_PATH,
            backups_directory=BACKUPS_DIRECTORY_PATH,
        )

    return ServerManager(
        compose_manager=None,
        docker_manager=docker_manager,
        data_manager=data_manager,
        server_registry=server_registry,
        backup_manager=backup_manager,
        game_manager_helpers=server_manager_helpers,
        compose_directory=COMPOSE_FILES_DIRECTORY_PATH,
        servers_directory=GAME_SERVERS_DIRECTORY_PATH,
        backups_directory=BACKUPS_DIRECTORY_PATH,
    )

server_registry_list = [
    SimpleNamespace(name="Test1",game="Minecraft",compose_file="path1"),
    SimpleNamespace(name="Test3",game="Minecraft",compose_file="path2"),
    SimpleNamespace(name="myServer",game="ArkSurvivalAscended",compose_file="path3"),
    SimpleNamespace(name="forestServer",game="TheForest",compose_file="path4")
]


async def test_nonexistence_check_pass(server_manager, server_registry):
    server_registry.get_servers.return_value = server_registry_list

    await server_manager.nonexistence_check("myServer2")

    server_registry.get_servers.assert_awaited_once()

async def test_nonexistence_check_raise(server_manager, server_registry):
    server_registry.get_servers.return_value = server_registry_list

    with pytest.raises(Exception):
        await server_manager.nonexistence_check("Test3")

    server_registry.get_servers.assert_awaited_once()

async def test_existence_check_pass(server_manager, server_registry):
    server_registry.get_servers.return_value = server_registry_list
    
    await server_manager.existence_check("myServer")

    server_registry.get_servers.assert_awaited_once()

async def test_existence_check_raise(server_manager, server_registry):
    server_registry.get_servers.return_value = server_registry_list

    with pytest.raises(Exception):
        await server_manager.existence_check("Test")

    server_registry.get_servers.assert_awaited_once()

async def test_container_check_pass(server_manager, docker_manager):
    docker_manager.container_exists.return_value = True

    await server_manager.container_check("Test")

    docker_manager.container_exists.assert_awaited_once_with("Test")

async def test_container_check_raise(server_manager, docker_manager):
    docker_manager.container_exists.return_value = False

    with pytest.raises(Exception):
        await server_manager.container_check("Test")

    docker_manager.container_exists.assert_awaited_once_with("Test")

async def test_online_check_pass(server_manager, docker_manager):
    docker_manager.is_online.return_value = True

    await server_manager.online_check("Test")

    docker_manager.is_online.assert_awaited_once_with("Test")

async def test_online_check_raise(server_manager, docker_manager):
    docker_manager.is_online.return_value = False

    
    with pytest.raises(Exception):
        await server_manager.online_check("Test")

    docker_manager.is_online.assert_awaited_once_with("Test")

async def test_offline_check_pass(server_manager, docker_manager):
    docker_manager.is_online.return_value = False

    await server_manager.offline_check("Test")

    docker_manager.is_online.assert_awaited_once_with("Test")

async def test_offline_check_raise(server_manager, docker_manager):
    docker_manager.is_online.return_value = True

    
    with pytest.raises(Exception):
        await server_manager.offline_check("Test")

    docker_manager.is_online.assert_awaited_once_with("Test")