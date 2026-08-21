

from discord.app_commands import Group
from abc import ABC, abstractmethod

from games.abstract.game_server_manager import GameServerManager


class Commands(ABC):
    def __init__(self, server_manager: GameServerManager):
        self.server_manager = server_manager
        self.group_name = server_manager.config.group_name
        self.game_name = server_manager.config.game_name

    # register commands
    @abstractmethod
    def register(self, group: Group):
        ...


        