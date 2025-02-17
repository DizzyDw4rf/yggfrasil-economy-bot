import discord
from discord import app_commands
from discord.ext import commands
from random import choice
from src.bot_status import BotStatus
from src.utils.constants import Constants
from src.databases import db_connection 


BotStatus.set_debug(True)
server = BotStatus.get_server()

class Games(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    async def send_inv_embed(self, interaction: discord.Interaction) -> discord.Embed:
        inv_embed = discord.Embed(
            title='Join our server',
            description=(
            f'You can Use the bot here: '
            f'[𝐘𝐆𝐆𝐃𝐑𝐀𝐒𝐈𝐋🌳](https://discord.gg/KDuf8kvJf4)'
            ),
            color=discord.Color.dark_green()
        )
        await interaction.response.send_message(embed=inv_embed)
    
    def create_embed(self, interaction: discord.Interaction, description: str, color: discord.Colour) -> discord.Embed:
        username = interaction.user.name
        icon = interaction.user.display_avatar
        em = discord.Embed(
            description=description,
            color=color
        )
        em.set_author(name=f"{username}", icon_url=icon)
        return em

    async def send_error_embed(self, interaction: discord.Interaction, title: str) -> discord.Embed:
        err_embed = discord.Embed(
            title=title,
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=err_embed, ephemeral=True)

    def get_user_data(self, user_id: int):
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT * FROM Users WHERE id = ?""", (user_id,))
            return c.fetchone()
    
    def update_user_wallet(self, user_id: int, wallet: int):
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("""UPDATE Users SET wallet = ? WHERE id = ?""", (wallet, user_id))
            conn.commit()    

    @app_commands.choices(
            face = [
                app_commands.Choice(name='Heads', value=Constants.COIN_HEAD),
                app_commands.Choice(name='Tails', value=Constants.COIN_TAILS)
            ]
    )
    @app_commands.command(name='coinflip', description="Gamble amount of credit from your wallet with a coin")
    async def coinflip(self, interaction: discord.Interaction, face: app_commands.Choice[str], amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
            return

        user_id = interaction.user.id
        user_data = self.get_user_data(user_id)

        amount = abs(amount)

        if user_data is None:
            await self.send_error_embed(interaction, title="User Not Found In Bank Database")
            return

        if amount > user_data[2] or amount == 0:
            await self.send_error_embed(interaction, title="Invalid Amount")
            return
        
        choices = [Constants.COIN_HEAD, Constants.COIN_TAILS]
        probability = choice(choices)

        if face.value == probability:
            new_wallet_balance = user_data[2] + amount
            self.update_user_wallet(user_id, new_wallet_balance)
            win_embed = self.create_embed(
                interaction,
                description=f"Your coin landed on {probability} You win {amount} {Constants.COIN}",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=win_embed)
        else:
            new_wallet_balance = user_data[2] - amount
            self.update_user_wallet(user_id, new_wallet_balance)
            lose_embed = self.create_embed(
                interaction,
                description=f"Your coin landed on {probability} You lost {amount} {Constants.COIN}",
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=lose_embed)


async def setup(client):
    await client.add_cog(Games(client))
