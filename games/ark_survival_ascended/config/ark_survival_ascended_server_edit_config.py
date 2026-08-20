from games.abstract.config.game_server_edit_config import GameServerEditConfig

from pydantic import Field


class ArkSurvivalAscendedServerEditConfig(GameServerEditConfig):
    game_port: int | None = Field(ge=1, le=65535)
    steam_port: int | None = Field(ge=1, le=65535)
    max_players: int| None = Field(ge=1, le=50)
    mods: str
