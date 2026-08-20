from pathlib import Path

from games.abstract.config.game_config import GameConfig



class TheForestConfig(GameConfig):
    game_name = "The Forest"
    command_name = "the-forest"
    system_name = "the_forest"
    group_name = "the-forest"
    compose_template = Path("the_forest/templates/compose.yml.j2")
    world_directories = [
        "saves",
    ]
    backup_no = 3