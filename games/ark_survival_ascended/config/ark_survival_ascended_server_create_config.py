from games.abstract.config.game_server_create_config import GameServerCreateConfig

from pydantic import Field
from typing import Literal


class ArkSurvivalAscendedServerCreateConfig(GameServerCreateConfig):
    game_port: int = Field(default=7777, ge=1, le=65535)
    steam_port: int = Field(default=27015, ge=1, le=65535)

    cluster_directory_path: str

    map_name: Literal[
        "TheIsland_WP",
        "ScorchedEarth_WP",
        "TheCenter_WP",
        "Aberration_WP",
        "Extinction_WP",
        "Ragnarok_WP",
        "Astraeos_WP",
        "Valguero_WP",
        "LostColony_WP",
        "Genesis_WP"
    ] = "TheIsland_WP"

    max_players: int = Field(default=5, ge=1, le=50)
    cluster_id: int
    mods: str