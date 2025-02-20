import discord
import config
import logging
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.bot_status import BotStatus
from src.services.embeds import EmbedService
from src.services.pagination import PaginationView


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("discord")

BotStatus.set_debug(False)
server = BotStatus.get_server()

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name='help', description="Show all the commands in the bot")
    async def help(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await EmbedService.send_inv_embed(interaction)
            return
        
        general_embed = EmbedService.create_embed(
            interaction,
            title="**General Economy Commands**",
            description=(
                f"1. </balance:1341783774819647571> Show you the credit you have in your wallet and bank and the total in both\n"
                f"2. </daily:1341783774819647575> You can use this command once a day to get a random amount of credit between 500, 100\n"
                f"3. </send:1341783774819647576> To send any member of the server amount of many you wish above 100 credits\n"
                f"4. </withdraw:1341783774819647577> To Take amount of credit from the your bank\n"
                f"5. </deposit:1341783774819647578> To save amount of credit in the bank from your wallet\n"
                f"6. </leaderboard:1341783774819647579> To Get a list of the top 10 rich people in the server\n"
                f"7. </gettax:1341783775234752552> To get info about server tax rate\n"
                f"8. </shop:1342204166382157997> To get a list of items you can buy\n"
                f"9. </itembuy:1342204166382157998> To buy an item from the shop\n"
                f"10. </collect_income:1342239167886790677> TO collect income based on roles you bought\n"
                f"11. </help:1341887672880336948> This command"
            )
        )

        games_embed = EmbedService.create_embed(
            interaction,
            title="**Games And Activity Commands**",
            description=(
                f"1. </coinflip:1341784147839942691> You can gamble amount of money with a 50/50 chance to double or lose the gambled amount\n"
                f"2. </work:1341784147839942692> You can use this command once every 30 mins to get a random amount of credit between 70 and 250\n"
                f"3. </crime:1341784147839942693> You can use this command once every 1 hour to try commiting a crime to get money but if you got caught you will pay a fine\n"
                f"4. </rob:1341784147839942694> You can use this command once every 4 hours to try stealing from someone in the server\n"
                f"5. </jackbot:1341837784582983803> You can use this command to play wiht the slot machine and get a chance to win a huge amount of credit with minimum of 10000 credits."
            )
        )
        
        admin_embed = EmbedService.create_embed(
            interaction,
            title="**Admin Only Commands**",
            description=(
                f"1. </add:1341783774819647572> To give a member amount of credit as you desire\n\n"
                f"2. </remove:1341783774819647573> To remove amount of credit as you desire\n\n"
                f"3. </settax:1341783775234752553> To change the tax rate of the economy system\n\n"
                f"4. </reset_economy:1341784147839942689> To reset the economy system\n\n"
                f"5. </reset_user:1341784147839942690> To reset a specific member"
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
