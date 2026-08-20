#!/usr/bin/env bash

set -euo pipefail

BOT_USER="discord-bot"
BOT_GROUP="discord-bot"

SERVICE_NAME="discord-game-server-manager"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
ENVIRONMENT_DIR="/etc/discord-game-server-manager"
ENVIRONMENT_FILE="${ENVIRONMENT_DIR}/environment"

if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root."
    exit 1
fi

: "${PROJECT_DIRECTORY:?PROJECT_DIRECTORY is not set}"
: "${SOURCE_ENV_FILE:?SOURCE_ENV_FILE is not set}"

: "${COMPOSE_FILES_DIRECTORY_PATH:?COMPOSE_FILES_DIRECTORY_PATH is not set}"
: "${GAME_SERVERS_DIRECTORY_PATH:?GAME_SERVERS_DIRECTORY_PATH is not set}"
: "${BACKUPS_DIRECTORY_PATH:?BACKUPS_DIRECTORY_PATH is not set}"

echo "Installing systemd service..."

#
# Install runtime environment file
#
mkdir -p "$ENVIRONMENT_DIR"

cp "$SOURCE_ENV_FILE" "$ENVIRONMENT_FILE"

chown root:root "$ENVIRONMENT_FILE"
chmod 600 "$ENVIRONMENT_FILE"

echo "Installed environment file:"
echo "  $ENVIRONMENT_FILE"

#
# Optional network binding
#
NETWORK_BINDING=""

if [[ -n "${NETWORK_INTERFACE:-}" ]]; then
    NETWORK_BINDING="BindToDevice=${NETWORK_INTERFACE}"
fi

#
# Create systemd service
#
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Discord Game Server Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple

User=$BOT_USER
Group=$BOT_GROUP
SupplementaryGroups=gameserver

WorkingDirectory=$PROJECT_DIRECTORY

EnvironmentFile=$ENVIRONMENT_FILE
Environment=PYTHONDONTWRITEBYTECODE=1

$NETWORK_BINDING

ExecStart=$PROJECT_DIRECTORY/.venv/bin/python $PROJECT_DIRECTORY/main.py

Restart=always
RestartSec=5

UMask=0007

# Hardening
NoNewPrivileges=false
PrivateTmp=true
ProtectSystem=strict

# The bot may only write to these locations.
ReadWritePaths=$COMPOSE_FILES_DIRECTORY_PATH
ReadWritePaths=$GAME_SERVERS_DIRECTORY_PATH
ReadWritePaths=$BACKUPS_DIRECTORY_PATH

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"

echo "Installed service:"
echo "  $SERVICE_FILE"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo "Systemd service installed."