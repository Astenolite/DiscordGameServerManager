#!/usr/bin/env bash

set -euo pipefail

BOT_USER="discord-bot"
BOT_GROUP="discord-bot"
GAME_GROUP="gameserver"

# Make sure the script is running as root.
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root."
    echo "Run it with sudo."
    exit 1
fi

# Require directory paths.
: "${COMPOSE_FILES_DIRECTORY_PATH:?COMPOSE_FILES_DIRECTORY_PATH is not set}"
: "${GAME_SERVERS_DIRECTORY_PATH:?GAME_SERVERS_DIRECTORY_PATH is not set}"
: "${BACKUPS_DIRECTORY_PATH:?BACKUPS_DIRECTORY_PATH is not set}"

# Make sure ACL tools are available.
if ! command -v setfacl >/dev/null 2>&1; then
    echo "ERROR: setfacl is not installed."
    echo "Install it with:"
    echo "  sudo apt install acl"
    exit 1
fi

echo "Configuring Discord Game Manager permissions..."

#
# Create groups
#
if ! getent group "$BOT_GROUP" >/dev/null; then
    echo "Creating group: $BOT_GROUP"
    groupadd --system "$BOT_GROUP"
else
    echo "Group already exists: $BOT_GROUP"
fi

if ! getent group "$GAME_GROUP" >/dev/null; then
    echo "Creating group: $GAME_GROUP"
    groupadd --system "$GAME_GROUP"
else
    echo "Group already exists: $GAME_GROUP"
fi

#
# Create bot user
#
if ! id "$BOT_USER" >/dev/null 2>&1; then
    echo "Creating user: $BOT_USER"

    useradd \
        --system \
        --gid "$BOT_GROUP" \
        --no-create-home \
        --shell /usr/sbin/nologin \
        "$BOT_USER"
else
    echo "User already exists: $BOT_USER"
fi

#
# Add bot to gameserver group
#
if id -nG "$BOT_USER" | grep -qw "$GAME_GROUP"; then
    echo "$BOT_USER is already a member of $GAME_GROUP"
else
    echo "Adding $BOT_USER to $GAME_GROUP"
    usermod -aG "$GAME_GROUP" "$BOT_USER"
fi

#
# Configure managed directories
#
configure_directory() {
    local dir="$1"

    echo "Configuring directory: $dir"

    # Create it if necessary.
    mkdir -p "$dir"

    #
    # Group ownership
    #

    # Give the gameserver group ownership of everything currently present.
    chgrp -R "$GAME_GROUP" "$dir"

    #
    # Standard Unix permissions
    #

    # Owner and gameserver group get read/write access.
    # Everyone else gets no access.
    chmod -R u+rwX,g+rwX,o-rwx "$dir"

    # New directories inherit the gameserver group.
    find "$dir" -type d -exec chmod g+s {} +

    #
    # ACL permissions
    #

    # Give the gameserver group full access to everything currently present.
    setfacl -R -m "g:${GAME_GROUP}:rwx" "$dir"

    # Make sure the ACL mask does not restrict gameserver permissions.
    setfacl -R -m "m::rwx" "$dir"

    # Configure default ACLs on every existing directory.
    #
    # Anything subsequently created inside these directories will inherit
    # access for the gameserver group. This is especially important for
    # files/directories created by Docker containers.
    find "$dir" -type d -exec \
        setfacl \
            -m "d:g:${GAME_GROUP}:rwx" \
            -m "d:m::rwx" \
            {} +

    echo "Configured: $dir"
}

configure_directory "$COMPOSE_FILES_DIRECTORY_PATH"
configure_directory "$GAME_SERVERS_DIRECTORY_PATH"
configure_directory "$BACKUPS_DIRECTORY_PATH"

echo
echo "Permission setup complete."
echo
echo "Bot user:     $BOT_USER"
echo "Bot group:    $BOT_GROUP"
echo "Game group:   $GAME_GROUP"
echo
echo "Managed directories:"
echo "  Compose:    $COMPOSE_FILES_DIRECTORY_PATH"
echo "  Servers:    $GAME_SERVERS_DIRECTORY_PATH"
echo "  Backups:    $BACKUPS_DIRECTORY_PATH"