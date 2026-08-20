from .minecraft.minecraft_server_manager import MinecraftServerManager
from .minecraft.minecraft_command_manager import MinecraftCommandManager

from .the_forest.the_forest_server_manager import TheForestServerManager
from .the_forest.the_forest_command_manager import TheForestCommandManager

from .ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager
from .ark_survival_ascended.ark_survival_ascended_command_manager import ArkSurvivalAscendedCommandManager

GAME_REGISTRY = {
    "Minecraft": (MinecraftServerManager, MinecraftCommandManager),
    "TheForest": (TheForestServerManager, TheForestCommandManager),
    "ArkSurvivalAscended": (ArkSurvivalAscendedServerManager, ArkSurvivalAscendedCommandManager)
    #"ark": ArkGame
}