import traceback
import discord

from discord import app_commands
from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.ark_survival_ascended.ark_survival_ascended_server_manager import ArkSurvivalAscendedServerManager


class ClusterCommands(Commands):
    def __init__(self, server_manager: ArkSurvivalAscendedServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="create-cluster",
            description="Create a cluster"
        )(self.create_cluster)

        group.command(
            name="delete-cluster",
            description="Delete a cluster"
        )(self.delete_cluster)
        


    async def create_cluster(
        self,
        interaction: discord.Interaction,
        cluster_name: str,
        cluster_id: app_commands.Range[int, 1, None],
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.create_cluster(cluster_name, cluster_id)

            await interaction.followup.send(f"Cluster `{cluster_name}` was created.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error creating cluster: `{e}`")

    async def delete_cluster(
        self,
        interaction: discord.Interaction,
        cluster_name: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.delete_cluster(cluster_name)

            await interaction.followup.send(f"Cluster `{cluster_name}` was sucessfully deleted.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error deleting cluster: `{e}`")

        