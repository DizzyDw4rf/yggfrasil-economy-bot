import discord
import config
import logging
from discord import app_commands
from discord.ext import commands
from src.utils.constants import Constants
from src.bot_status import BotStatus
from src.services.databases import DatabaseService
from src.services.embeds import EmbedService


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("discord")

BotStatus.set_debug(False)
server = BotStatus.get_server()

class Shop(commands.Cog):

    def __init__(self, client):
        self.client = client

    def get_user_data(self, user_id: int):
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT * FROM Users WHERE id = ?""", (user_id,))
            return c.fetchone()
    
    def update_user_wallet(self, user_id: int, wallet: int):
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""UPDATE Users SET wallet = ? WHERE id = ?""", (wallet, user_id))
            conn.commit()    

    @app_commands.command(name="shop", description="Shows the items inside shop")
    async def shop(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await EmbedService.send_inv_embed(interaction)
            return
        
        shop_embed = EmbedService.create_embed(
            interaction,
            title=f"**{interaction.guild.name}'s Shop**",
            description=(
                f"Buy an item with the /itembuy command.\n"
            ),
            color=discord.Colour.dark_blue()
        )
        shop_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

        for item, value in Constants.SHOP.items():
            shop_embed.add_field(
                name=f"**{item} {Constants.COIN}:**",
                value=f"{value[0]}",
                inline=False
            )
        
        await interaction.response.send_message(embed=shop_embed)

    @app_commands.choices(
        item_name = [app_commands.Choice(name=name, value=name) for name in Constants.SHOP.keys()]
    )
    @app_commands.command(name='itembuy', description="Use to buy an item from the shop")
    async def itembuy(self, interaction: discord.Interaction, item_name: app_commands.Choice[str]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await EmbedService.send_inv_embed(interaction)
            return

        user_id = interaction.user.id
        user_data = self.get_user_data(user_id)

        guild = interaction.guild
        user = interaction.user

        item_price = Constants.SHOP[item_name.name][1]

        if user_data[2] < item_price:
            await interaction.response.send_message(f"You don't have {item_name.name} price, you can't buy it.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        role = discord.utils.get(guild.roles, name=f"{item_name.name}")
        if role is None:
            role = await guild.create_role(name=f"{item_name.name}")
        
        if role not in user.roles:
            await user.add_roles(role)
            new_wallet_balance = user_data[2] - item_price
            self.update_user_wallet(user_id, new_wallet_balance)
            bought_embed = EmbedService.create_embed(
                interaction,
                title="**Item bought succsessfully**",
                description=f"You got yourself the role <@&{role.id}>",
                color=discord.Colour.yellow()
            )
            bought_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
            await interaction.followup.send(embed=bought_embed)
        else:
            embed = discord.Embed(description="You already have this role", color=discord.Color.dark_red())
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(client):
    await client.add_cog(Shop(client))
