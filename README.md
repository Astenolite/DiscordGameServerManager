# Discord Game Server Manager

A Discord bot for managing Docker-hosted game servers through Discord commands instead of having to interact with them directly through the shell.

The goal of the project is to provide a common interface for basic game-server management while still allowing individual games to implement their own behavior, commands, and directory structures.

> [!NOTE]
> This project is still a work in progress. It is functional and has a number of useful features, but there is still plenty of cleanup, refactoring, and development to be done.

## Features

All supported servers expose a set of general management commands:

* `/server start` — Start a server.
* `/server stop` — Stop a server.
* `/server restart` — Restart a server.
* `/server query` — Display information about the current state of a server.
* `/server list` — List the available servers.

Each game module also provides commands for managing its servers:

* `/server create`
* `/server delete`
* `/server edit`
* `/server backup`
* `/server restore`
* `/server list-backups`
* `/server reset`

Individual game modules can also expose their own game-specific commands and behavior.

Use:

`/server <game_name>`

in Discord to see the commands currently provided by a particular game module.

A complete list of game-specific commands is not currently maintained here. This may be added in a future update; for now, Discord's command discovery is the best way to see what a module supports.

## Game Modules

The bot is designed around game modules.

Each module is responsible for deciding how servers for that game are managed, including things such as:

* Server configuration
* Directory structure
* Docker Compose configuration
* Backups and restores
* Game-specific functionality

This allows games with very different server-management requirements to still be controlled through the same Discord bot.

At the moment, some examples of game-specific behavior include:

### ARK: Survival Ascended

ARK servers can be organized into **clusters** and have support for managing **mods**.

This is an example of a game module requiring additional concepts beyond simply creating and starting an individual server.

### Minecraft

Minecraft servers provide game-specific commands for managing server operators, including:

* `make_op`
* `remove_op`

These features are mainly intended to demonstrate how individual modules can extend the bot with functionality specific to their game.

More game-specific functionality may be added over time.

## Docker Image Credits

This project relies on third-party Docker images for running the supported game servers. **I did not create or maintain these images.** Credit belongs to their respective creators and contributors.

| Game                   | Docker Image                  | Creator / Source                                                                                                                    |
| ---------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Minecraft              | `itzg/minecraft-server`       | [itzg/docker-minecraft-server](https://github.com/itzg/docker-minecraft-server)                                                     |
| ARK: Survival Ascended | `mschnitzer/asa-linux-server` | [mschnitzer/ark-survival-ascended-linux-container-image](https://github.com/mschnitzer/ark-survival-ascended-linux-container-image) |
| The Forest             | `justmiles/the-forest`        | [justmiles/the-forest on Docker Hub](https://hub.docker.com/r/justmiles/the-forest)                                                 |

If additional third-party images are used by this project in the future, their creators will be credited here as well.


## Installation

### Requirements

The project is currently designed to run with:

* **Python 3.12**
* **Docker**
* **Docker Compose**
* A Discord bot/application and its bot token
* A Linux-based host

The required Python libraries are listed in `requirements.txt`.

Currently, installation is handled through the project's setup script.

First, create a `.env` file based on the provided example and add your Discord bot token.

For example:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

Then run the setup script provided by the project.

The setup process prepares the environment required by the bot, including its game-server storage directories and helper scripts.

> [!WARNING]
> The installation/setup process is not yet as modular as I would like it to be. Currently, game modules are installed as part of the project even if you do not intend to use those games.


## Server Data and Permissions

By default, the bot creates and manages its own space under:

```text
/srv/GameServer
```

Game-server files, Compose files, backups, and other data managed by the bot are kept within the directories intended for the project.

### Sudo Helper Scripts

Some of the Docker images used by this project have their own users, ownership rules, and permission setups. This can make managing their files directly from the Discord bot difficult.

To work around this, the setup process installs a small number of helper scripts that the bot is allowed to execute using `sudo`.

These scripts are intentionally restricted to operating within directories belonging to the game-server manager rather than providing the bot with unrestricted root access.

The helper scripts can be inspected in the project's `scripts` directory.

If you are installing this project on your own machine, **you are strongly encouraged to review these scripts and the associated sudo permissions yourself before running the bot.**

## Project Status

This project is **not finished**.

It has reached a point where it is functional and demonstrates the overall idea, but there are several areas I would still like to improve.

Some future work may include:

* Cleaning up and refactoring the existing code.
* Making it easier to create and integrate new game modules.
* Removing or configuring parameters that are currently hardcoded.
* Making installation more modular.
* Allowing users to install only the game modules they actually need.
* Expanding game-specific functionality.
* Improving documentation for game-specific commands.

There is no guarantee that the current interfaces, configuration formats, or project structure will remain unchanged while the project is still under development.

## Architecture

The project is intentionally built so that game modules can make their own decisions about how a particular game should be managed rather than forcing every game into exactly the same structure.

This README does not attempt to document the complete internal architecture.

If you are interested in how the bot, game modules, Docker Compose management, configuration, backups, and filesystem handling work internally, the project source is the best reference.

## Disclaimer

This is a personal, work-in-progress project and should be treated accordingly.

Before running it on a system containing important game-server data, review the configuration, Docker Compose files, helper scripts, filesystem permissions, and backup behavior yourself.

**Back up any existing server data before experimenting with the project.**
