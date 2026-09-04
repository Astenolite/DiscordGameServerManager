import subprocess
import json
import docker
import asyncio

from datetime import datetime, timezone
from pathlib import Path
from docker.models.containers import Container

def parse_docker_timestamp(timestamp: str) -> datetime:
    if "." in timestamp:
        base, fraction = timestamp.rstrip("Z").split(".", 1)
        fraction = fraction[:6].ljust(6, "0")
        return datetime.fromisoformat(f"{base}.{fraction}+00:00")

    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

class DockerManager:

    def __init__(self):
        self.client = docker.from_env()


    async def get_container(self, container_name: str) -> Container:
        container = await asyncio.to_thread(
            self.client.containers.get,
            container_name,
        )
        return container

    async def container_exists(self, container_name: str) -> bool:
        if await self.get_container(container_name) is None:
            return False
        return True
    
    async def container_isOnline(self, container_name: str) -> bool:
        if not await self.container_exists(container_name):
            raise ValueError(f"Container {container_name} does not exist")

        container = self.get_container(container_name)
    
    async def create(self, compose_file: Path) -> None:
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "create"
            ],
            check=True,
        )

    async def compose_up(self, compose_file: Path) -> None:
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "up",
                "-d",
                "--wait",
            ],
            check=True,
        )
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "stop"
            ],
            check=True
        )
    
    async def compose_down(self, compose_file: Path) -> None:
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "down",
                "-v",
            ],
            check=True,
        )

    """
    async def is_online(self, container_name: str) -> bool:
        if not await self.container_exists(container_name):
            return False
        
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format={{.State.Running}}",
                container_name,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() == "true"
    
    async def start(self, container_name: str):
        container = await self.get_container(container_name)
        container.start()
    """

    async def stop(self, container_name: str):
        container = await self.get_container(container_name)
        container.stop()

    async def restart(self, container_name: str):
        container = await self.get_container(container_name)
        container.restart()

    async def status(self, container_name) -> dict:
        container = await self.get_container(container_name)

        result = container.status
        print(container.status, flush=True)

        container = json.loads(result.stdout)[0]
        state = container["State"]

        created = parse_docker_timestamp(container["Created"])
        started_at = parse_docker_timestamp(state["StartedAt"])

        finished_at = None

        if (
            state.get("FinishedAt")
            and not state["FinishedAt"].startswith("0001-01-01")
        ):
            finished_at = parse_docker_timestamp(state["FinishedAt"])

        return {
            "name": container["Name"].lstrip("/"),
            "created": int(created.timestamp()),
            "running": state["Running"],
            "status": state["Status"],
            "started_at": int(started_at.timestamp()),
            "finished_at": (
                int(finished_at.timestamp())
                if finished_at
                else None
            ),
            "health": state.get("Health", {}).get("Status"),
        }
    
    async def execute_command(self, container_name: str, command: list[str]) -> int:
        container = await self.get_container(container_name)
        result = container.exec_run(command)
        return result.exit_code

    async def get_container_image(self, container_name: str) -> str:
        container = await self.get_container(container_name)
        image = container.attrs["Config"]["Image"]
        image_name = image.rsplit(":", 1)[0]
        return image_name