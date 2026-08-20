import shutil
import asyncio

from pathlib import Path

from core.data_manager import DataManager


class BackupManager():

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    # take all files/directories whose path is (active_directory_path / active_data[i]) and copy them in (backup_directory_path / backup_name / active_date[i])
    async def backup_server(self, active_directory_path: Path, active_data: list[str], backup_directory_path: Path, backup_name: str,):
        backup_path = Path(backup_directory_path / backup_name)

        for path in active_data:
            active_data_path = (active_directory_path / path)
            backup_data_path = (backup_path / path)

            if active_data_path.is_dir():
                await self.data_manager.copy_directory(
                    source=str(active_data_path),
                    destination=str(backup_data_path)
                )
            else:
                await self.data_manager.copy_file(
                    source=str(active_data_path),
                    destination=str(backup_data_path)
                )

        return backup_path

    # for all files in (backup_directory_path / backup_name) copy them to (active_directory_path) keeping same relative oredering
    async def restore_server(self, backup_directory_path: Path, active_directory_path: Path, backup_name: str):
        backup_path = (backup_directory_path / backup_name)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup {backup_name} does not exist")

        active_directory_path.mkdir(parents=True, exist_ok=True)

        for backup_file_path in backup_path.rglob("*"):
            # Directories will be created automatically when needed.
            if not backup_file_path.is_file():
                continue

            # Get path relative to the backup root.
            relative_path = backup_file_path.relative_to(backup_path)

            # Preserve that same path in the restore directory.
            restore_file_path = active_directory_path / relative_path
            print(f"Old file {restore_file_path} -- New file {backup_file_path}", flush=True)

            await self.data_manager.replace_file(
                old_file=restore_file_path, 
                new_file=backup_file_path
            )

    #
    async def delete_backup(self, backup_directory_path: Path, backup_name: str):
        backup_path = (backup_directory_path / backup_name)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup {backup_name} does not exist")

        await self.data_manager.delete_directory(backup_path)
        
    # get list of all backup directories
    def get_backups(self, backup_directory_path: Path) -> list[str]:
        if not backup_directory_path.exists():
            return []
        
        backups = []

        for backup in backup_directory_path.iterdir():
            if backup.is_dir():
                backups.append(backup.name)

        return backups