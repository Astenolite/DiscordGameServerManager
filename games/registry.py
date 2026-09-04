from .minecraft.minecraft_server_manager import MinecraftServerManager
from .minecraft.minecraft_command_manager import MinecraftCommandManager
from .minecraft.server_manager_helper import ServerManagerHelper as MinecraftServerManagerHelper

from .the_forest.the_forest_server_manager import TheForestServerManager
from .the_forest.the_forest_command_manager import TheForestCommandManager
from .the_forest.server_manager_helper import ServerManagerHelper as TheForestServerManagerHelper

from .ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager
from .ark_survival_ascended.ark_survival_ascended_command_manager import ArkSurvivalAscendedCommandManager
from .ark_survival_ascended.server_manager_helper import ServerManagerHelper as ArkSurvivalAscendedServerManagerHelper

GAME_REGISTRY = [
    {
        "name": "Minecraft", 
        "image": "itzg/minecraft-server", 
        "server_manager_helper": MinecraftServerManagerHelper,
        "server_manager_extra": MinecraftServerManager, 
        "command_manager": MinecraftCommandManager,
    },
    {
        "name": "TheForest", 
        "image": "justmiles/the-forest", 
        "server_manager_helper": TheForestServerManagerHelper,
        "server_manager_extra": TheForestServerManager, 
        "command_manager": TheForestCommandManager,
    },
    {
        "name": "ArkSurvivalAscended", 
        "image": "mschnitzer/asa-linux-server", 
        "server_manager_helper": ArkSurvivalAscendedServerManagerHelper,
        "server_manager_extra": ArkSurvivalAscendedServerManager, 
        "command_manager": ArkSurvivalAscendedCommandManager,
    },
]