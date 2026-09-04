import json

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from core.data_manager import DataManager

class ComposeManager:
    def __init__(self, templates_directory: Path, data_manager: DataManager):
        self._environment = Environment(
            loader=FileSystemLoader(templates_directory),
            undefined=StrictUndefined,
            autoescape=False,
        )

        self.data_manager = data_manager

    # Creates compose file
    def render(self, template_path: str, output_path: Path, context: dict) -> None:
        template = self._environment.get_template(template_path)

        # Render first. If Jinja fails, nothing has been created on disk yet.
        content = template.render(**context)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        context_file = output_path.parent / "context.json"

        temporary_compose_file = output_path.with_suffix(
            output_path.suffix + ".tmp"
        )

        temporary_context_file = context_file.with_suffix(
            context_file.suffix + ".tmp"
        )

        try:
            
            # Write compose file to temporary file.
            temporary_compose_file.write_text(
                content,
                encoding="utf-8",
            )

            # Write context to temporary JSON file.
            self.data_manager.create_context_file(context_file, context)

            # Only replace the real files after both writes succeeded.
            temporary_compose_file.replace(output_path)
            temporary_context_file.replace(context_file)

        except Exception:
            temporary_compose_file.unlink(missing_ok=True)
            temporary_context_file.unlink(missing_ok=True)
            raise

    # Edits existing compose file
    def edit(self, template_path: str, existing_file: Path, new_context: dict):
        context_file = existing_file.parent / "context.json"

        if not existing_file.exists():
            raise FileNotFoundError(
                f"Compose file does not exist: {existing_file}"
            )

        if not context_file.exists():
            raise FileNotFoundError(
                f"Context file does not exist: {context_file}"
            )

        # Load the context originally used to create the compose file.
        context = self.data_manager.read_context_file(context_file)

        # Replace only the values supplied in the new context.
        context.update(new_context)

        # Re-render the compose file and update context.json.
        self.render(
            template_path=template_path,
            output_path=existing_file,
            context=context,
        )


