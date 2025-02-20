import discord
import config
import logging
from discord import app_commands
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, Button
from datetime import datetime
from src.bot_status import BotStatus
from src.services.embeds import EmbedService
from src.services.databases import DatabaseService


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("discord")

BotStatus.set_debug(False)
server = BotStatus.get_server()

class Admin(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    def get_user_data(self, user_id: int):
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT * FROM Users WHERE id = ?""", (user_id,))
            return c.fetchone()

    def update_user(self, user_id: int, wallet: int, bank: int) -> None:
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""UPDATE Users SET wallet = ?, bank = ? WHERE id = ?""", (wallet, bank, user_id))
            conn.commit()

    @app_commands.command(name='reset_economy', description="Reset all the balances of users to default values.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_economy(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await EmbedService.send_inv_embed(interaction)
            return

        user_id = interaction.user.id

        reset_bal_embed = discord.Embed(
            title="**Resetting All Economy System**",
            description=(
                f"Are you sure you want to reset all the balance of the users to it's default value?\n\n"
                f"This Action cannot be `reversed`, Press confirm to proceed or cancel to abort"
                f"```This message will be deleted after 5 mins if no action taken.```"
            ),
            color=discord.Color.dark_blue(),
            timestamp=datetime.now()
        )
        reset_bal_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)

        confirm_btn = Button(
            style=ButtonStyle.primary,
            label="Confirm",
            emoji="✔"
        )
        cancel_btn = Button(
            style=ButtonStyle.danger,
            label="Cancel",
            emoji="✖"
        )

        reset_economy_view = View()
        reset_economy_view.add_item(confirm_btn)
        reset_economy_view.add_item(cancel_btn)
        await interaction.response.send_message(embed=reset_bal_embed, view=reset_economy_view, delete_after=300)
    
        async def reset_econmoy_confirm_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not the command user!", ephemeral=True)
                return
            
            with DatabaseService.db_connection() as conn:
                c = conn.cursor()
                c.execute("""DELETE FROM Users""")
                c.execute("""DELETE FROM Transactions""")
                c.execute("""DELETE FROM sqlite_sequence WHERE name = 'Transactions'""")
                conn.commit()

            reset_success = discord.Embed(
                title="**Resetting All Economy System**",
                description="Economy System has been reset Successfully!",
                color=discord.Colour.green(),
                timestamp=datetime.now()
            )
            reset_success.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)
            logger.info(f"{interaction.user.name} has reset the server economy system")
            await interaction.response.edit_message(embed=reset_success, view=None, delete_after=1.5)
        
        async def reset_econmoy_cancel_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not the command user!", ephemeral=True)
                return
            
            canceld_embed = discord.Embed(
                title="**Resetting All Economy System**",
                description="Economy System reset Canceld",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            canceld_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)
            logger.info(f"{interaction.user.name} Canceld restting balance system")
            await interaction.response.edit_message(embed=canceld_embed, view=None, delete_after=1.5)
        
        confirm_btn.callback = reset_econmoy_confirm_callback
        cancel_btn.callback = reset_econmoy_cancel_callback

    @reset_economy.error
    async def reset_economy_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            em = discord.Embed(
                description=f"{interaction.user.mention} You have to be an Adminstrator to use this Command.",
                color=discord.Color.dark_red()
            )
            logger.error(f"{interaction.user.name} Tried to use /reset_economy command while he not adminstartor")
            await interaction.response.send_message(embed=em, ephemeral=True)

    @app_commands.command(name="reset_user", description="Reset the balance of the user to default")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_user(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await EmbedService.send_inv_embed(interaction)
            return
        
        user_id = interaction.user.id

        member_id = member.id
        member_data = self.get_user_data(member_id)

        if member.guild_permissions.administrator:
            await interaction.response.send_message("You can't reset an administrator", ephemeral=True)
            return

        if member_data is None:
            await interaction.response.send_message("This User don't have bank Account", ephemeral=True)
            return

        confirm_btn = Button(
            style=ButtonStyle.primary,
            label="Confirm",
            emoji="✔"
        )
        cancel_btn = Button(
            style=ButtonStyle.danger,
            label="Cancel",
            emoji="✖"
        )
        reset_user_embed = discord.Embed(
            title=f"Resetting {member.name}'s Balance",
            description=(
                f"Are you sure you want to reset {member.mention}'s Balance to the default value\n\n"
                f"This Action cannot be `reversed`, Press Confirm to proceed or Cancel to abort\n\n"
                f"```This message will be deleted after 5 mins if no action taken.```"
            ),
            colour=discord.Color.dark_blue(),
            timestamp=datetime.now()
        )
        reset_user_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)

        reset_user_view = View()
        reset_user_view.add_item(confirm_btn)
        reset_user_view.add_item(cancel_btn)

        await interaction.response.send_message(embed=reset_user_embed, view=reset_user_view, delete_after=300)

        async def reset_user_confirm_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not the command user!", ephemeral=True)
                return

            self.update_user(member_id, 500, 500)

            confirm_embed = discord.Embed(
                title=f"Resetting {member.name}'s Balance",
                description=f"{member.mention}'s Balance been reset Successfully!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            confirm_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)

            logger.info(f"{interaction.user.name} has reset {member.name} balance")
            await interaction.response.edit_message(embed=confirm_embed, view=None, delete_after=1.5)

        async def reset_user_cancel_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not the command user!", ephemeral=True)
                return
            
            cancel_embed = discord.Embed(
                title=f"Resetting {member.name}'s Balance",
                description=f"{member.mention}'s Balance reset Canceld!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            cancel_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)

            logger.info(f"{interaction.user.name} canceled resetting {member.name} balance")
            await interaction.response.edit_message(embed=cancel_embed, view=None, delete_after=1.5)
        
        confirm_btn.callback = reset_user_confirm_callback
        cancel_btn.callback = reset_user_cancel_callback
    
    @reset_user.error
    async def reset_user_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            em = discord.Embed(
                description=f"{interaction.user.mention} You have to be an Adminstrator to use this Command.",
                color=discord.Color.dark_red()
            )
            logger.error(f"{interaction.user.name} Tried to use /reset_user command while he not adminstartor")
            await interaction.response.send_message(embed=em, ephemeral=True)


async def setup(client):
    await client.add_cog(Admin(client))
