#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="/etc/discord-game-server-manager/environment"

if [[ $# -ne 2 ]]; then
    echo "Usage: replace_file.sh <target_file> <replacement_file>" >&2
    exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Environment file not found: $ENV_FILE" >&2
    exit 1
fi

source "$ENV_FILE"

TARGET="$1"
SOURCE="$2"

if [[ ! -f "$SOURCE" ]]; then
    echo "ERROR: Replacement file does not exist: $SOURCE" >&2
    exit 1
fi

SOURCE="$(realpath "$SOURCE")"

TARGET_PARENT="$(dirname "$TARGET")"
TARGET_NAME="$(basename "$TARGET")"

# Find the nearest existing parent directory.
EXISTING_PARENT="$TARGET_PARENT"

while [[ ! -d "$EXISTING_PARENT" ]]; do
    NEXT_PARENT="$(dirname "$EXISTING_PARENT")"

    if [[ "$NEXT_PARENT" == "$EXISTING_PARENT" ]]; then
        echo "ERROR: Could not find an existing parent directory for: $TARGET" >&2
        exit 1
    fi

    EXISTING_PARENT="$NEXT_PARENT"
done

EXISTING_PARENT="$(realpath "$EXISTING_PARENT")"

# Reconstruct the full target path from the existing parent.
RELATIVE_PARENT="${TARGET_PARENT#"$EXISTING_PARENT"}"
TARGET="$EXISTING_PARENT$RELATIVE_PARENT/$TARGET_NAME"

ALLOWED_DIRECTORIES=(
    "$COMPOSE_FILES_DIRECTORY_PATH"
    "$GAME_SERVERS_DIRECTORY_PATH"
    "$BACKUPS_DIRECTORY_PATH"
    "$TESTS_DIRECTORY_PATH"
)

TARGET_ALLOWED=false
SOURCE_ALLOWED=false

for directory in "${ALLOWED_DIRECTORIES[@]}"; do
    ALLOWED_DIRECTORY="$(realpath "$directory")"

    if [[ "$TARGET" == "$ALLOWED_DIRECTORY"/* ]]; then
        TARGET_ALLOWED=true
    fi

    if [[ "$SOURCE" == "$ALLOWED_DIRECTORY"/* ]]; then
        SOURCE_ALLOWED=true
    fi
done

if [[ "$TARGET_ALLOWED" != true ]]; then
    echo "ERROR: Target file is outside all allowed directories: $TARGET" >&2
    exit 1
fi

if [[ "$SOURCE_ALLOWED" != true ]]; then
    echo "ERROR: Replacement file is outside all allowed directories: $SOURCE" >&2
    exit 1
fi

if [[ -f "$TARGET" ]]; then
    # Existing file: overwrite in place.
    cp -f -- "$SOURCE" "$TARGET"
    exit 0
fi

# Get ownership from the nearest existing directory.
OWNER_UID="$(stat -c '%u' "$EXISTING_PARENT")"
OWNER_GID="$(stat -c '%g' "$EXISTING_PARENT")"

# Create missing parent directories.
mkdir -p -- "$TARGET_PARENT"

# Apply the inherited ownership to the newly created directory tree.
CURRENT="$TARGET_PARENT"

while [[ "$CURRENT" != "$EXISTING_PARENT" ]]; do
    chown "$OWNER_UID:$OWNER_GID" "$CURRENT"
    CURRENT="$(dirname "$CURRENT")"
done

# Copy the file.
cp -- "$SOURCE" "$TARGET"

# Give the new file the same ownership.
chown "$OWNER_UID:$OWNER_GID" "$TARGET"