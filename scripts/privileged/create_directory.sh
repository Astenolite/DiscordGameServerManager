#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="/etc/discord-game-server-manager/environment"

if [[ $# -ne 1 ]]; then
    echo "Usage: create_directory.sh <directory>" >&2
    exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Environment file not found: $ENV_FILE" >&2
    exit 1
fi

source "$ENV_FILE"

TARGET="$1"

ALLOWED_DIRECTORIES=(
    "$COMPOSE_FILES_DIRECTORY_PATH"
    "$GAME_SERVERS_DIRECTORY_PATH"
    "$BACKUPS_DIRECTORY_PATH"
)

TARGET="$(realpath -m "$TARGET")"

for directory in "${ALLOWED_DIRECTORIES[@]}"; do
    ALLOWED_DIRECTORY="$(realpath "$directory")"

    if [[ "$TARGET" == "$ALLOWED_DIRECTORY"/* ]]; then
        mkdir -p -- "$TARGET"
        exit 0
    fi
done

echo "ERROR: Directory is outside all allowed directories: $TARGET" >&2
exit 1