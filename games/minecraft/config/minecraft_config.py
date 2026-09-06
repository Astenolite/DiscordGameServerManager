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
    startup_string = "Thread RCON Listener started"
    java_versions = [
        {
            "min_minecraft": "1.12",
            "max_minecraft": "1.16.5",
            "container_java": "java8" 
        },
        {
            "min_minecraft": "1.17",
            "max_minecraft": "1.17.1",
            "container_java": "java16" 
        },
        {
            "min_minecraft": "1.18",
            "max_minecraft": "1.20.4",
            "container_java": "java17" 
        },
        {
            "min_minecraft": "1.20.5",
            "max_minecraft": "1.21.11",
            "container_java": "java21" 
        },
        {
            "min_minecraft": "1.20.5",
            "max_minecraft": "2", # latest version
            "container_java": "java25" 
        },
    ]
    save_command = ["rcon-cli", "save-all", "flush"]