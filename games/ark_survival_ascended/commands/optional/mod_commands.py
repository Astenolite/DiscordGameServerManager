import traceback
import discord

from typing_extensions import Literal

from discord import app_commands
from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ModCommands(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="add-mod",
            description="Adds a mod to a cluster"
        )(self.add_mod)

        group.command(
            name="remove-mod",
            description="Removes a mod from a cluster"
        )(self.remove_mod)

        group.command(
            name="list-mods",
            description="Lists all mods from a cluster"
        )(self.list_mods)

        


    async def add_mod(
        self,
        interaction: discord.Interaction,
        cluster_name: str,
        mod_id: int,
        mod_name: str,
        mod_type: Literal[
            "QoL",
            "+ Structures",
            "+ Animal",
            "TLC Animal",
        ]
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.add_mod(cluster_name, mod_id, mod_name, mod_type)

            await interaction.followup.send(f"Mod `{mod_id}` was added to cluster {cluster_name}.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error adding mod: `{e}`")

    async def remove_mod(
        self,
        interaction: discord.Interaction,
        cluster_name: str,
        mod_id: int
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.remove_mod(cluster_name, mod_id)

            await interaction.followup.send(f"Mod `{mod_id}` was removed from cluster {cluster_name}.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error removing mod: `{e}`")

    async def list_mods(
        self,
        interaction: discord.Interaction,
        cluster_name: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            mod_list = await self.server_manager.list_mods(cluster_name)

            if not mod_list:
                await interaction.followup.send(
                    f"No mods found for cluster `{cluster_name}`."
                )
                return

            # Sort by mod type, then alphabetically by mod name
            mod_list.sort(
                key=lambda mod: (mod[2].lower(), mod[1].lower())
            )

            embed = discord.Embed(
                title=f"Mods — {cluster_name}",
                description=f"**{len(mod_list)} mod(s) installed**",
                color=discord.Color.blurple(),
            )

            # Group mods by type
            mods_by_type = {}
            print(mod_list, flush=True)

            for mod_id, mod_name, mod_type in mod_list:
                mods_by_type.setdefault(mod_type, []).append(
                    (mod_id, mod_name)
                )

            for mod_type, mods in mods_by_type.items():
                lines = [
                    f"**{mod_name}** — {mod_type} (`{mod_id}`)"
                    for mod_id, mod_name in mods
                ]

                embed.add_field(
                    name=mod_type,
                    value="\n".join(lines),
                    inline=False,
                )

            await interaction.followup.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error finding mods: `{e}`")

        