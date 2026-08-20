import traceback
import discord

from discord.app_commands import Group

from games.abstract.commands.commands import Commands

from games.minecraft.minecraft_server_manager import MinecraftServerManager


class MinecraftCommands(Commands):
    def __init__(self, server_manager: MinecraftServerManager):
        super().__init__(server_manager)


    def register(self, group: Group):
        group.command(
            name="make-op",
            description="Give server operator privileges"
        )(self.make_op)

        group.command(
            name="remove-op",
            description="Remove server operator privileges"
        )(self.remove_op)
        


    async def make_op(
        self,
        interaction: discord.Interaction,
        server_name: str,
        account: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.make_op(server_name, account)

            await interaction.followup.send(f"`{account}` was made an operator of `{server_name}`.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error executing command: `{e}`")

    async def remove_op(
        self,
        interaction: discord.Interaction,
        server_name: str,
        account: str,
    ): 
        await interaction.response.defer(thinking=True)

        try:
            await self.server_manager.remove_op(server_name, account)

            await interaction.followup.send(f"`{account}` was removed from the operators of `{server_name}`.")
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(f"Error executing command: `{e}`")

        