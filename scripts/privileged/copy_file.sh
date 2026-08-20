#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="/etc/discord-game-server-manager/environment"

if [[ $# -ne 2 ]]; then
    echo "Usage: copy_file.sh <source> <destination>" >&2
    exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Environment file not found: $ENV_FILE" >&2
    exit 1
fi

source "$ENV_FILE"

SOURCE="$1"
DESTINATION="$2"

if [[ ! -f "$SOURCE" ]]; then
    echo "ERROR: Source file does not exist: $SOURCE" >&2
    exit 1
fi

SOURCE="$(realpath "$SOURCE")"
DESTINATION="$(realpath -m "$DESTINATION")"

ALLOWED_DIRECTORIES=(
    "$COMPOSE_FILES_DIRECTORY_PATH"
    "$GAME_SERVERS_DIRECTORY_PATH"
    "$BACKUPS_DIRECTORY_PATH"
)

SOURCE_ALLOWED=false
DESTINATION_ALLOWED=false

for directory in "${ALLOWED_DIRECTORIES[@]}"; do
    ALLOWED_DIRECTORY="$(realpath "$directory")"

    if [[ "$SOURCE" == "$ALLOWED_DIRECTORY"/* ]]; then
        SOURCE_ALLOWED=true
    fi

    if [[ "$DESTINATION" == "$ALLOWED_DIRECTORY"/* ]]; then
        DESTINATION_ALLOWED=true
    fi
done

if [[ "$SOURCE_ALLOWED" != true ]]; then
    echo "ERROR: Source file is outside all allowed directories: $SOURCE" >&2
    exit 1
fi

if [[ "$DESTINATION_ALLOWED" != true ]]; then
    echo "ERROR: Destination is outside all allowed directories: $DESTINATION" >&2
    exit 1
fi

mkdir -p -- "$(dirname "$DESTINATION")"

cp -f -- "$SOURCE" "$DESTINATION"