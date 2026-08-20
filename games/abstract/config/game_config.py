import re
from pathlib import Path
from typing import ClassVar

_NAME_PATTERN = re.compile(r"^[a-z_-]+$")


class GameConfig:
    game_name: ClassVar[str]
    command_name: ClassVar[str]
    group_name: ClassVar[str]
    system_name: ClassVar[str]
    compose_template: ClassVar[Path]
    world_directories: ClassVar[list[str]]
    backup_no: ClassVar[int]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        required_fields = (
            "game_name",
            "command_name",
            "group_name",
            "system_name",
            "compose_template",
            "world_directories",
            "backup_no",
        )

        for field_name in required_fields:
            if not hasattr(cls, field_name):
                raise TypeError(
                    f"{cls.__name__} must define {field_name!r}"
                )

        for field_name in ("group_name", "system_name"):
            value = getattr(cls, field_name)

            if not isinstance(value, str):
                raise TypeError(
                    f"{cls.__name__}.{field_name} must be a str"
                )

            if not 1 <= len(value) <= 32:
                raise ValueError(
                    f"{cls.__name__}.{field_name} must be between "
                    f"1 and 32 characters"
                )

            if not _NAME_PATTERN.fullmatch(value):
                raise ValueError(
                    f"{cls.__name__}.{field_name} may only contain "
                    "lowercase letters, '_' and '-'"
                )

        if not isinstance(cls.game_name, str) or not cls.game_name:
            raise ValueError(
                f"{cls.__name__}.game_name must be a non-empty string"
            )

        if not isinstance(cls.compose_template, Path):
            raise TypeError(
                f"{cls.__name__}.compose_template must be a Path"
            )