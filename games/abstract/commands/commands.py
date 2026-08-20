

from discord.app_commands import Group
from abc import ABC, abstractmethod

from games.abstract.game_server_manager import GameServerManager


class Commands(ABC):

    @abstractmethod
    def __init__(self, server_manager: GameServerManager):
        self.server_manager = server_manager

    # register commands
    @abstractmethod
    def register(self, group: Group):
        ...


        