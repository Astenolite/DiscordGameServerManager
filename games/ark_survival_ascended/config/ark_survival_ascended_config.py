from pathlib import Path

from games.abstract.config.game_config import GameConfig

class ArkSurvivalAscendedConfig(GameConfig):
    game_name = "ArkSurvivalAscended"
    command_name = "ark-survival-ascended"
    system_name = "ark_survival_ascended"
    group_name = "ark-survival-ascended"
    compose_template = Path("ark_survival_ascended/templates/compose.yml.j2")
    world_directories = [
        "ShooterGame/Saved/SavedArks",
        "ShooterGame/Saved/Config/WindowsServer",
    ]
    backup_no = 5
    startup_string = "fsync: up and running."
    save_command = ["asa-ctrl", "rcon", "--exec", "saveworld"]
