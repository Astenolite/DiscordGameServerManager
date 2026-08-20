#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIRECTORY="$(cd "$SCRIPT_DIRECTORY/.." && pwd)"
PRIVILEGED_SOURCE_DIRECTORY="$SCRIPT_DIRECTORY/privileged"

BOT_USER="discord-bot"

ENV_FILE="$PROJECT_DIRECTORY/.env"

PRIVILEGED_INSTALL_DIRECTORY="/usr/local/libexec/discord-game-server-manager"
PRIVILEGED_CONF_DIRECTORY="/etc/discord-game-server-manager"
SUDOERS_FILE="/etc/sudoers.d/discord-game-server-manager"

HELPERS=(
    "delete_directory.sh"
    "delete_file.sh"
    "clear_directory.sh"
    "replace_file.sh"
    "copy_file.sh"
    "copy_directory.sh"
    "create_directory.sh"
)





echo "=========================================="
echo " Discord Game Server Manager Setup"
echo "=========================================="
echo

#
# Must run as root
#
if [[ $EUID -ne 0 ]]; then
    echo "This setup script requires root privileges."
    echo
    echo "Please run:"
    echo
    echo "  sudo ./scripts/setup.sh"
    echo
    exit 1
fi

#
# Check .env
#
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: Configuration file not found:"
    echo
    echo "  $ENV_FILE"
    echo
    echo "Create it first:"
    echo
    echo "  cp .env.example .env"
    echo
    echo "Then edit .env and run setup again."
    exit 1
fi

echo "Using configuration:"
echo "  $ENV_FILE"
echo

#
# Load configuration
#
set -a
source "$ENV_FILE"
set +a

#
# Validate required configuration
#
: "${DISCORD_TOKEN:?DISCORD_TOKEN is not set}"
: "${COMPOSE_FILES_DIRECTORY_PATH:?COMPOSE_FILES_DIRECTORY_PATH is not set}"
: "${GAME_SERVERS_DIRECTORY_PATH:?GAME_SERVERS_DIRECTORY_PATH is not set}"
: "${BACKUPS_DIRECTORY_PATH:?BACKUPS_DIRECTORY_PATH is not set}"

#
# Require absolute paths
#
validate_absolute_path() {
    local name="$1"
    local value="$2"

    if [[ "$value" != /* ]]; then
        echo "ERROR: $name must be an absolute path."
        echo "Current value:"
        echo "  $value"
        echo
        echo "Do not use ~ in paths."
        exit 1
    fi
}

validate_absolute_path \
    "COMPOSE_FILES_DIRECTORY_PATH" \
    "$COMPOSE_FILES_DIRECTORY_PATH"

validate_absolute_path \
    "GAME_SERVERS_DIRECTORY_PATH" \
    "$GAME_SERVERS_DIRECTORY_PATH"

validate_absolute_path \
    "BACKUPS_DIRECTORY_PATH" \
    "$BACKUPS_DIRECTORY_PATH"


#
# Permission setup
#
echo
echo "------------------------------------------"
echo "Setting up users and permissions"
echo "------------------------------------------"
echo

"$SCRIPT_DIRECTORY/initialize/give_permissions.sh"

#
# Privileged helper installation
#
echo
echo "------------------------------------------"
echo "Installing privileged helpers"
echo "------------------------------------------"
echo




for helper in "${HELPERS[@]}"; do
    PRIVILEGED_HELPER_SOURCE="$PRIVILEGED_SOURCE_DIRECTORY/$helper"
    if [[ ! -f "$PRIVILEGED_HELPER_SOURCE" ]]; then
        echo "ERROR: Privileged helper not found: $PRIVILEGED_HELPER_SOURCE"
        exit 1
    fi
done

mkdir -p "$PRIVILEGED_INSTALL_DIRECTORY"

chown root:root "$PRIVILEGED_INSTALL_DIRECTORY"
chmod 0755 "$PRIVILEGED_INSTALL_DIRECTORY"

for helper in "${HELPERS[@]}"; do
    install \
        --owner=root \
        --group=root \
        --mode=0755 \
        "$PRIVILEGED_SOURCE_DIRECTORY/$helper" \
        "$PRIVILEGED_INSTALL_DIRECTORY/$helper"

    echo "Installed:"
    echo "  $PRIVILEGED_INSTALL_DIRECTORY/$helper"
done

echo "Installed:"

#
# Sudo configuration
#
echo
echo "Configuring sudo permissions..."

# Start with an empty file.
: > "$SUDOERS_FILE"

for helper in "${HELPERS[@]}"; do
    echo \
        "$BOT_USER ALL=(root) NOPASSWD: $PRIVILEGED_INSTALL_DIRECTORY/$helper" \
        >> "$SUDOERS_FILE"
done

chmod 0440 "$SUDOERS_FILE"

if ! visudo -cf "$SUDOERS_FILE"; then
    echo "ERROR: Invalid sudoers configuration."
    rm -f "$SUDOERS_FILE"
    exit 1
fi

echo "Installed sudoers configuration:"
echo "  $SUDOERS_FILE"

#
# Service installation
#
echo
echo "------------------------------------------"
echo "Installing systemd service"
echo "------------------------------------------"
echo

export PROJECT_DIRECTORY
export SOURCE_ENV_FILE="$ENV_FILE"

"$SCRIPT_DIRECTORY/initialize/install_service.sh"

#
# Start bot
#
echo
echo "------------------------------------------"
echo "Starting bot"
echo "------------------------------------------"
echo

systemctl restart discord-game-server-manager.service

echo
echo "=========================================="
echo " Setup complete"
echo "=========================================="
echo
echo "Service status:"
echo

systemctl --no-pager --full status discord-game-server-manager.service || true

echo
echo "Useful commands:"
echo
echo "  Status:"
echo "    sudo systemctl status discord-game-server-manager"
echo
echo "  Restart:"
echo "    sudo systemctl restart discord-game-server-manager"
echo
echo "  Stop:"
echo "    sudo systemctl stop discord-game-server-manager"
echo
echo "  Logs:"
echo "    sudo journalctl -u discord-game-server-manager -f"
echo