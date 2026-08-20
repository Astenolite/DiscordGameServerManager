from pathlib import Path

from games.abstract.config.game_config import GameConfig



class MinecraftConfig(GameConfig):
    game_name = "Minecraft"
    command_name = "minecraft"
    system_name = "minecraft"
    group_name = "minecraft"
    compose_template = Path("minecraft/templates/compose.yml.j2")
    world_directories = [
        "data/world",
        "data/world_nether",
        "data/world_the_end"
    ]
    backup_no = 5