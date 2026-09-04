import datetime

import discord
import traceback
from discord.ext import commands



class ServerBackupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_manager = bot.server_manager

    def register(self):
        self.bot.server_group.command(
            name="backup",
            description="Backup server"
        )(self.backup_server)

        self.bot.server_group.command(
            name="list-backups",
            description="List server backups"
        )(self.list_backups)

        self.bot.server_group.command(
            name="delete-backup",
            description="Delete server backup"
        )(self.delete_backup)

        self.bot.server_group.command(
            name="restore",
            description="restore server backup"
        )(self.restore_backup)

    
    async def backup_server(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)
    
        try:
            await self.server_manager.backup_server(server_name)

            await interaction.followup.send(f"Server `{server_name}` backed up successfully.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error backing up server: `{e}`")

    async def list_backups(self, interaction: discord.Interaction, server_name: str):
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
            await interaction.followup.send(f"Error listing backups for server: `{e}`")



    async def delete_backup(self, interaction: discord.Interaction, server_name: str, backup_name: str):
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.delete_backup(server_name, backup_name)

            await interaction.followup.send(f"Backup `{backup_name}` deleted sucessfully")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error deleting backup: `{e}`")


    async def restore_backup(self, interaction: discord.Interaction, server_name: str, backup_name: str = None):
        await interaction.response.defer(thinking=True)
        
        try:
            self.server_manager.restore_backup(server_name, backup_name)

            await interaction.followup.send(f"Server `{server_name}` sucessfully restored")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error restoring backup: `{e}`")

    
        
async def setup(bot):
    cog = ServerBackupCommands(bot)

    cog.register()

    await bot.add_cog(cog)
