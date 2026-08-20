from games.abstract.config.game_server_create_config import GameServerCreateConfig

from pydantic import Field
from typing import Literal


class MinecraftServerCreateConfig(GameServerCreateConfig):
    port: int = Field(default=25565, ge=1, le=65535)

    server_type: Literal[
        "VANILLA",
        "SPIGOT",
        "FABRIC",
        "FORGE",
        "PAPER",
    ] = "VANILLA"

    version: str = "LATEST"

    memory: int = Field(default=4, ge=1)

    max_players: int = Field(default=10, ge=1,)

    online_mode: bool = True

    difficulty: Literal[
        "peaceful",
        "easy",
        "normal",
        "hard",
    ] = "normal"

    render_distance: int = Field(default=16, ge=4, le=64)
