#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="/etc/discord-game-server-manager/environment"

if [[ $# -ne 1 ]]; then
    echo "Usage: clear_directory.sh <directory>" >&2
    exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Environment file not found: $ENV_FILE" >&2
    exit 1
fi

source "$ENV_FILE"

TARGET="$1"

if [[ ! -d "$TARGET" ]]; then
    echo "ERROR: Directory does not exist: $TARGET" >&2
    exit 1
fi

TARGET="$(realpath "$TARGET")"

ALLOWED_DIRECTORIES=(
    "$COMPOSE_FILES_DIRECTORY_PATH"
    "$GAME_SERVERS_DIRECTORY_PATH"
    "$BACKUPS_DIRECTORY_PATH"
    "$TESTS_DIRECTORY_PATH"
)

ALLOWED=false

for directory in "${ALLOWED_DIRECTORIES[@]}"; do
    ALLOWED_DIRECTORY="$(realpath "$directory")"

    if [[ "$TARGET" == "$ALLOWED_DIRECTORY"/* ]]; then
        ALLOWED=true
        break
    fi
done

if [[ "$ALLOWED" != true ]]; then
    echo "ERROR: Directory is outside all allowed directories: $TARGET" >&2
    exit 1
fi

find "$TARGET" \
    -mindepth 1 \
    -maxdepth 1 \
    -exec rm -rf -- {} +