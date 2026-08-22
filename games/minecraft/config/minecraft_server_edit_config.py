from games.abstract.config.game_server_edit_config import GameServerEditConfig

from pydantic import Field
from typing import Literal


class MinecraftServerEditConfig(GameServerEditConfig):
    port: int | None = Field(ge=1, le=65535)

    server_type: Literal[
        "VANILLA",
        "SPIGOT",
        "FABRIC",
        "FORGE",
        "PAPER",
    ] | None

    version: str | None
    java_version: str | None

    memory: int | None = Field(ge=1)

    max_players: int | None = Field(ge=1)

    online_mode: bool | None

    difficulty: Literal[
        "peaceful",
        "easy",
        "normal",
        "hard",
    ] | None

    render_distance: int | None = Field(ge=4, le=64)
