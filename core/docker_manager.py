import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path

def parse_docker_timestamp(timestamp: str) -> datetime:
    if "." in timestamp:
        base, fraction = timestamp.rstrip("Z").split(".", 1)
        fraction = fraction[:6].ljust(6, "0")
        return datetime.fromisoformat(f"{base}.{fraction}+00:00")

    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

class DockerManager:
    
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
    

    async def compose_down(self, compose_file: Path):
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

    async def container_exists(self, container_name: str) -> bool:
        result = subprocess.run(
            [
                "docker", 
                "container", 
                "inspect", 
                container_name
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return result.returncode == 0

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
        subprocess.run(
            [
                "docker",
                "start",
                container_name
            ],
            check=True
        )

    async def stop(self, container_name: str):
        subprocess.run(
            [
                "docker",
                "stop",
                container_name
            ],
            check=True
        )

    async def restart(self, container_name):
        subprocess.run(
            [
                "docker",
                "restart",
                container_name
            ],
            check=True
        )

    async def status(self, container_name) -> dict:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                container_name,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

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
    
    async def execute_command(self, container_name: str, command: list[str]):
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                *command
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return result.stdout.strip()
        

        