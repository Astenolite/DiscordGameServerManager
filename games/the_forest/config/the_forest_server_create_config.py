from games.abstract.config.game_server_create_config import GameServerCreateConfig

from pydantic import Field
from typing import Literal


class TheForestServerCreateConfig(GameServerCreateConfig):
    port1: int = Field(default=8766, ge=1, le=65535)
    port2: int = Field(default=27015, ge=1, le=65535)
    port3: int = Field(default=27016, ge=1, le=65535)

    server_steam_account: str
    max_players: int = 5
    server_password: str = ""
    server_admin_password: str = "admin"

    difficulty: Literal[
        "Peaceful",
        "Normal",
        "Hard"
    ] = "Normal"
