import subprocess
import json

from pathlib import Path


class DataManager:
    def __init__(self):
        ...

    async def create_directory(self, directory_path: str):
        if Path(directory_path).exists():
            return

        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/create_directory.sh",
                directory_path,
            ],
            check=True
        )

    async def create_context_file(self, file_path: Path, context: dict):
        context_file = file_path / "context.json"
        temporary_context_file = context_file.with_suffix(context_file.suffix + ".tmp")

        try:
            temporary_context_file.write_text(
                json.dumps(
                    context,
                    indent=4,
                ),
                encoding="utf-8",
            )

            temporary_context_file.replace(context_file)
        except Exception as e:
            temporary_context_file.unlink(missing_ok=True)
            raise

    async def read_context_file(self, context_directory: str) -> dict:
        context_file = context_directory / "context.json"

        if not context_file.exists():
            raise FileNotFoundError(f"{context_file} file does not exist.")

        context = json.loads(
            Path(context_file).read_text(encoding="utf-8")
        )

        return context

    async def edit_context_file(self, context_file_path: str, context: dict):
        old_context = await self.read_context_file(context_file_path)
        new_context = old_context | context
        await self.create_context_file(context_file_path, new_context)

    async def delete_directory(self, directory_path: str):
        if not Path(directory_path).exists():
            return
        
        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/delete_directory.sh",
                directory_path,
            ],
            check=True,
        )

    async def delete_file(self, file_path: str):
        if not Path(file_path).exists():
            return
        
        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/delete_file.sh",
                file_path
            ],
            check=True,
        )

    async def clear_directory(self, directory_path: str):
        if not Path(directory_path).exists():
            return

        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/clear_directory.sh",
                directory_path
            ],
            check=True,
        )

    async def replace_file(self, old_file: str, new_file: str):
        if not Path(new_file).exists():
            return

        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/replace_file.sh",
                old_file,
                new_file,
            ],
            check=True,
        )

    async def copy_directory(self, source: str, destination: str):
        if not Path(source).exists():
            return

        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/copy_directory.sh",
                source,
                destination
            ],
            check=True,       
        )

    async def copy_file(self, source: str, destination: str):
        if not Path(source).exists():
            return

        subprocess.run(
            [
                "sudo",
                "/usr/local/libexec/discord-game-server-manager/copy_file.sh",
                source,
                destination
            ],
            check=True,
        )

    async def file_exists(self, file_path: str) -> bool:
        return Path(file_path).is_file()

    async def directory_exists(self, directory_path: str) -> bool:
        return Path(directory_path).is_dir()