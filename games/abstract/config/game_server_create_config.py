from pydantic import BaseModel, Field


class GameServerCreateConfig(BaseModel):

    server_name: str = Field(
            min_length=1,
            max_length=64,
            pattern=r"^[a-zA-Z0-9_-]+$",
        )

    compose_directory_path: str
    compose_file: str
    container_directory_path: str