import asyncio
import json
import subprocess
import docker
import time

from datetime import datetime
from pathlib import Path
from docker.errors import NotFound
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
        try:
            return await asyncio.to_thread(
                self.client.containers.get,
                container_name,
            )
        except NotFound as e:
            raise ValueError(f"Container {container_name} does not exist") from e
        
    async def container_exists(self, container_name: str) -> bool:
        try:
            await asyncio.to_thread(
                self.client.containers.get,
                container_name,
            )
            return True
        except NotFound:
            return False

    async def container_isOnline(self, container_name: str) -> bool:
        if not await self.container_exists(container_name):
            return False

        container = await self.get_container(container_name)

        # Docker SDK Container objects cache their state,
        # so reload before checking the current status.
        await asyncio.to_thread(container.reload)

        return container.status == "running"

    async def create(self, compose_file: Path) -> None:
        await asyncio.to_thread(
            subprocess.run,
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "create",
            ],
            check=True,
        )

    async def compose_up(self, compose_file: Path) -> None:
        await asyncio.to_thread(
            subprocess.run,
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

        await asyncio.to_thread(
            subprocess.run,
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "stop",
            ],
            check=True,
        )

    async def compose_down(self, compose_file: Path) -> None:
        await asyncio.to_thread(
            subprocess.run,
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

    async def docker_logs(self, container_name: str, tail: int | str = "all") -> str:
        container = await self.get_container(container_name)

        logs = await asyncio.to_thread(
            container.logs,
            stdout=True,
            stderr=True,
            tail=tail,
        )

        return logs.decode(
            "utf-8",
            errors="replace",
        )

    async def start(self, container_name: str, startup_string: str | None = None, timeout: int = 600, check_interval: float = 0.5) -> None:
        container = await self.get_container(container_name)

        # Record this BEFORE starting so we don't miss very early logs.
        started_at = int(time.time()) - 1

        await asyncio.to_thread(container.start)

        if startup_string is None:
            return

        deadline = asyncio.get_running_loop().time() + timeout

        while True:
            await asyncio.to_thread(container.reload)

            if container.status != "running":
                logs = await asyncio.to_thread(
                    container.logs,
                    stdout=True,
                    stderr=True,
                    since=started_at,
                )

                logs = logs.decode(
                    "utf-8",
                    errors="replace",
                )

                raise RuntimeError(
                    f"Container {container_name} stopped during startup.\n"
                    f"Logs:\n{logs[-5000:]}"
                )

            logs = await asyncio.to_thread(
                container.logs,
                stdout=True,
                stderr=True,
                since=started_at,
            )

            decoded_logs = logs.decode(
                "utf-8",
                errors="replace",
            )

            if startup_string in decoded_logs:
                return

            if asyncio.get_running_loop().time() >= deadline:
                raise TimeoutError(
                    f"Container {container_name} did not finish startup "
                    f"within {timeout} seconds.\n"
                    f"Waiting for: {startup_string!r}\n"
                    f"Last logs:\n{decoded_logs[-5000:]}"
                )

            await asyncio.sleep(check_interval)

    async def stop(self, container_name: str) -> None:
        container = await self.get_container(container_name)

        await asyncio.to_thread(container.stop)

    async def restart(self, container_name: str, startup_string: str | None = None, timeout: int = 600) -> None:
        container = await self.get_container(container_name)

        await asyncio.to_thread(container.restart)

        if startup_string is None:
            return

        try:
            await asyncio.wait_for(
                asyncio.to_thread(
                    self._wait_for_startup_log,
                    container,
                    startup_string,
                ),
                timeout=timeout,
            )

        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Container {container_name} did not finish startup within {timeout} seconds.") from e

    async def status(self, container_name: str) -> dict:
        container = await self.get_container(container_name)

        await asyncio.to_thread(container.reload)

        attributes = container.attrs
        state = attributes["State"]

        created = parse_docker_timestamp(
            attributes["Created"]
        )

        started_at = parse_docker_timestamp(
            state["StartedAt"]
        )

        finished_at = None

        if (
            state.get("FinishedAt")
            and not state["FinishedAt"].startswith("0001-01-01")
        ):
            finished_at = parse_docker_timestamp(
                state["FinishedAt"]
            )

        return {
            "name": attributes["Name"].lstrip("/"),
            "created": int(created.timestamp()),
            "running": state["Running"],
            "status": state["Status"],
            "started_at": int(started_at.timestamp()),
            "finished_at": (
                int(finished_at.timestamp())
                if finished_at
                else None
            ),
            "health": state.get(
                "Health",
                {},
            ).get("Status"),
        }

    async def execute_command(self, container_name: str, command: list[str]) -> int:
        container = await self.get_container(container_name)

        result = await asyncio.to_thread(
            container.exec_run,
            command,
        )

        return result.exit_code

    async def get_container_image(self, container_name: str) -> str:
        container = await self.get_container(container_name)

        await asyncio.to_thread(container.reload)

        image = container.attrs["Config"]["Image"]

        return image.rsplit(":", 1)[0]