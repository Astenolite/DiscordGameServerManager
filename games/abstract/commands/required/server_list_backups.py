import traceback
import discord

from datetime import datetime
from discord.app_commands import Group
from games.abstract.commands.commands import Commands


class ServerListBackups(Commands):

    def register(self, group: Group):
        group.command(
            name=f"{self.group_name}",
            description=f"List available backups for an {self.game_name} server"
        )(self.list_backups)


    async def list_backups(
        self,
        interaction: discord.Interaction,
        server_name: str
    ): 
        await interaction.response.defer(thinking=True)

        try:
            backups_list = await self.server_manager.list_backups(server_name)

            if not backups_list:
                embed = discord.Embed(
                    title="📦 Backups",
                    description=f"No backups found for **{server_name}**.",
                    color=discord.Color.orange(),
                )

                await interaction.followup.send(embed=embed)
                return

            # Newest backup first
            backups_list.sort(reverse=True)

            backup_lines = []

            for index, backup_name in enumerate(backups_list, start=1):
                try:
                    backup_date = datetime.strptime(
                        backup_name,
                        "Backup_%Y-%m-%d-%H-%M",
                    )

                    formatted_date = backup_date.strftime(
                        "%d %B %Y at %H:%M"
                    )

                    backup_lines.append(
                        f"`{index:02}.` **{formatted_date}**\n"
                        f"     `{backup_name}`"
                    )

                except ValueError:
                    # In case a manually named backup exists
                    backup_lines.append(
                        f"`{index:02}.` `{backup_name}`"
                    )

            embed = discord.Embed(
                title=f"📦 Backups — {server_name}",
                description="\n\n".join(backup_lines),
                color=discord.Color.blue(),
            )

            embed.set_footer(
                text=f"{len(backups_list)} backup{'s' if len(backups_list) != 1 else ''} available"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error finding backups for server: `{e}`")

        