from games.abstract.config.game_server_edit_config import GameServerEditConfig

from pydantic import Field
from typing import Literal


class TheForestServerEditConfig(GameServerEditConfig):
    port1: int | None = Field(ge=1, le=65535) 
    port2: int | None = Field(ge=1, le=65535) 
    port3: int | None = Field(ge=1, le=65535) 

    server_steam_account: str | None
    max_players: int | None
    server_password: str | None
    server_admin_password: str | None

    difficulty: Literal[
        "Peaceful",
        "Normal",
        "Hard"
    ] | None