
from pathlib import Path

from dataclasses import dataclass

@dataclass
class GameServer:
    name: str
    game: str
    compose_file: Path

class ServerRegistry:
    def __init__(self, compose_directory: Path):
        self.compose_directory = Path(compose_directory)

    def get_servers(self) -> list[GameServer]:
        servers = []

        for game_directory in self.compose_directory.iterdir():
            if not game_directory.is_dir():
                continue

            for compose_file in game_directory.rglob("*.yml"):
                servers.append(
                    GameServer(
                        name=compose_file.stem,
                        game=game_directory.name,
                        compose_file=compose_file,
                    )
                )

        return servers

