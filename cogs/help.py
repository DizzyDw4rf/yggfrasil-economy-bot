import discord
import config
import logging
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.bot_status import BotStatus
from src.services.pagination import PaginationView


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("discord")

BotStatus.set_debug(False)
server = BotStatus.get_server()

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def send_inv_embed(self, interaction) -> discord.Embed:
        inv_embed = discord.Embed(
            title='Join our server',
            description=(
            f'You can Use the bot here: '
            f'[𝐘𝐆𝐆𝐃𝐑𝐀𝐒𝐈𝐋🌳](https://discord.gg/KDuf8kvJf4)'
            ),
            color=discord.Color.dark_green()
        )
        await interaction.response.send_message(embed=inv_embed)

    def create_embed(self, interaction: discord.Interaction, title: str, description: str) -> discord.Embed:
        user = interaction.user.name
        icon = interaction.user.display_avatar
        em = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        em.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
        em.set_footer(text=f"Used by: {user}", icon_url=icon)
        return em

    @app_commands.command(name='help', description="Show all the commands in the bot")
    async def help(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        general_embed = self.create_embed(
            interaction,
            title="**General Economy Commands**",
            description=(
                f"1. `/balance` Show you the credit you have in your wallet and bank and the total in both\n\n"
                f"2. `/daily` You can use this command once a day to get a random amount of credit between 500, 100\n\n"
                f"3. `/send` To send any member of the server amount of many you wish above 100 credits\n\n"
                f"4. `/withdraw` To Take amount of credit from the your bank\n\n"
                f"5. `/deposite` To save amount of credit in the bank from your wallet\n\n"
                f"6. `/leaderboard` To Get a list of the top 10 rich people in the server\n\n"
                f"7. `/gettax` To get info about server tax rate\n\n"
                f"8. `/help` This command\n\n"
            ),
        )

        games_embed = self.create_embed(
            interaction,
            title="**Games And Activity Commands**",
            description=(
                f"1. `/coinflip` You can gamble amount of money with a 50/50 chance to double or lose the gambled amount\n\n"
                f"2. `/work` You can use this command once every 30 mins to get a random amount of credit between 70 and 250\n\n"
                f"3. `/crime` You can use this command once every 1 hour to try commiting a crime to get money but if you got caught you will pay a fine\n\n"
                f"4. `/rob` You can use this command once every 4 hours to try stealing from someone in the server\n\n"
                f"5. `/jackbot` You can use this command to play wiht the slot machine and get a chance to win a huge amount of credit with minimum of 10000 credits."
            )
        )
        
        admin_embed = self.create_embed(
            interaction,
            title="**Admin Only Commands**",
            description=(
                f"1. `/add` To give a member amount of credit as you desire\n\n"
                f"2. `/remove` To remove amount of credit as you desire\n\n"
                f"3. `/settax` To change the tax rate of the economy system\n\n"
                f"4. `/reset_economy` To reset the economy system\n\n"
                f"5. `/reset_user` To reset a specific member\n\n"
            )
        )

        embeds = [
            general_embed,
            games_embed,
            admin_embed,
        ]
        async def get_page(index: int) -> tuple:
            total_pages = len(embeds)
            return embeds[index - 1], total_pages

        view = PaginationView(interaction, get_page)
        await view.navegate()


async def setup(client):
    await client.add_cog(Help(client))
