import discord
import logging
import config
from datetime import datetime
from discord import ButtonStyle
from discord.ui import View, Button
from discord import app_commands
from discord.ext import commands
from random import choice, randint
from src.bot_status import BotStatus
from src.utils.constants import Constants
from src.services.databases import DatabaseService
from src.services.slot_machine import SlotMachineService


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("discord")

BotStatus.set_debug(False)
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
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT * FROM Users WHERE id = ?""", (user_id,))
            return c.fetchone()
    
    def update_user_wallet(self, user_id: int, wallet: int):
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""UPDATE Users SET wallet = ? WHERE id = ?""", (wallet, user_id))
            conn.commit()    

    @app_commands.choices(
            face = [
                app_commands.Choice(name=f'Heads', value=Constants.COIN_HEAD),
                app_commands.Choice(name=f'Tails', value=Constants.COIN_TAILS)
            ]
    )
    @app_commands.command(name='coinflip', description="Gamble amount of credit from your wallet with a coin")
    async def coinflip(self, interaction: discord.Interaction, face: app_commands.Choice[str], amount: app_commands.Range[int, 10]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return

        user_id = interaction.user.id
        user_data = self.get_user_data(user_id)

        if user_data is None:
            await self.send_error_embed(interaction, title="User Not Found In Bank Database")
            return

        if amount > user_data[2]:
            await self.send_error_embed(interaction, title="You don't have Enough credits in your wallet")
            return
        
        choices = [f"Heads {Constants.COIN_HEAD} ", f"Tails {Constants.COIN_TAILS}"]
        probability = choice(choices)

        if face.value == probability:
            new_wallet_balance = user_data[2] + amount
            description=f"Your coin landed on {probability} You win {amount} {Constants.COIN}"
            color=discord.Color.yellow()
        else:
            new_wallet_balance = user_data[2] - amount
            description=f"Your coin landed on {probability} You lost {amount} {Constants.COIN}"
            color=discord.Color.dark_red()
        
        self.update_user_wallet(user_id, new_wallet_balance) # Updating user wallet
        cf_embed = self.create_embed(interaction, description=description, color=color)
        await interaction.response.send_message(embed=cf_embed)

    @app_commands.command(name='work', description="Do a work and get paid with credit")
    @app_commands.checks.cooldown(1, 1800, key=lambda i: i.user.id)
    async def work(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return

        user_id = interaction.user.id
        user_data = self.get_user_data(user_id)

        if user_data is None:
            await self.send_error_embed(interaction, title="User Not Found In Bank Database")
            return
        
        choices = choice(Constants.WORK_REPLIES) # Getting a random reply
        rand_amt = randint(70, 250) # Getting a random payment to update wallet with

        new_wallet_balance = user_data[2] + rand_amt

        self.update_user_wallet(user_id, new_wallet_balance) # Updating user wallet

        work_embed = self.create_embed(
            interaction,
            description=f"{choices} And get Paid with {rand_amt} {Constants.COIN}",
            color=discord.Color.dark_orange()
        )
        await interaction.response.send_message(embed=work_embed)

    @work.error
    async def work_error(self, interaction: discord.Interaction, error) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after, 2) # Time remaining in seconds
            minutes = (remaining_time % 1800) // 60 
            cd_embed = discord.Embed(
                title="**⏰ You are in timeout!**",
                description=f"You can't work for `{minutes}` minutes",
                colour=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=cd_embed, ephemeral=True)

    @app_commands.command(name='crime', description="Commit A crime to get credit but if you got caught you will pay fine")
    @app_commands.checks.cooldown(1, 3600, key=lambda i: i.user.id)
    async def crime(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        user_id = interaction.user.id
        user_data = self.get_user_data(user_id)

        if user_data is None:
            await self.send_error_embed(interaction, title="User Not Found In Bank Database")
            return
        
        choices = choice(Constants.CRIME_REPLIES) # Getting a random crime reply
        fine_amt = randint(400, 700) 
        earn_amt = randint(250, 400)

        probability = randint(1, 3) # Setting a 1/3 prob

        if probability == 3: # Setting 3 as the caught prob
            if fine_amt >= user_data[2]: # Making sure not to put user in dept by setting wallet to 0 if fine > wallet
                new_wallet_balance = 0
                description=f'{choices} But you got caught and Paied all you have as fine your {Constants.WALLET} 0 {Constants.COIN}'
                color=discord.Colour.dark_red()
            else:
                new_wallet_balance = user_data[2] - fine_amt
                description=f'{choices} But you got caught and Paid {fine_amt} {Constants.COIN}'
                color=discord.Color.dark_red()
        else:
            new_wallet_balance = user_data[2] + earn_amt
            description=f'{choices} You have earned {earn_amt} {Constants.COIN}'
            color=discord.Color.yellow()

        self.update_user_wallet(user_id, new_wallet_balance) # Updating user wallet
        crime_embed = self.create_embed(interaction, description=description, color=color)
        await interaction.response.send_message(embed=crime_embed)

    @crime.error
    async def crime_error(self, interaction: discord.Interaction, error) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after, 2) # Remaining time in seconds
            minutes = (remaining_time % 3600) // 60
            cd_embed = discord.Embed(
                title=f"**⏰ You are in timeout!**",
                description=f"You can't commit a crime before `{minutes}` minutes",
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=cd_embed, ephemeral=True)

    @app_commands.command(name='rob', description='Try to steal from a member in guild')
    @app_commands.checks.cooldown(1, 14400, key=lambda i : i.user.id)
    async def rob(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        user_id = interaction.user.id
        member_id = member.id
        user_data = self.get_user_data(user_id)
        member_data = self.get_user_data(member_id)

        if user_data is None or member_data is None:
            await self.send_error_embed(interaction, title="User Or Member choosen not found In Bank Database")
            return
        
        if user_id == member_id:
            await self.send_error_embed(interaction, title="You can't rob Yourself\nNow wait `4` hours to use command again!")
            return
        
        rob_quantity = randint(200, 1000)
        rob_success_prob = randint(1, 3) # Setting 1/3 prob

        if rob_success_prob == 3:
            if rob_quantity >= member_data[2]: # If robbed money >= member money in the wallet give all to the robber and set wallet of robbed to 0
                new_member_wallet_bal = 0
                new_user_wallet_bal = user_data[2] + member_data[2]
                description=f"{interaction.user.mention} has robbed all {Constants.COIN} from {member.mention}'s wallet"
                color=discord.Colour.dark_gold()
            else:
                new_member_wallet_bal = member_data[2] - rob_quantity
                new_user_wallet_bal = user_data[2] + rob_quantity
                description=f"{interaction.user.mention} has robbed {rob_quantity} {Constants.COIN} from {member.mention}"
                color=discord.Colour.dark_gold()
        else:
            if rob_quantity >= user_data[2]: # If robbed money >= user money in the wallet set user wallet to 0 and give member all money
                new_member_wallet_bal = user_data[2] + member_data[2]
                new_user_wallet_bal = 0
                description=f"{interaction.user.mention} tried to rob {member.mention} and failed\n\n{member.mention} took all money in {interaction.user.mention} wallet"
                color=discord.Color.dark_red()
            else:    
                new_member_wallet_bal = member_data[2] + rob_quantity
                new_user_wallet_bal = user_data[2] - rob_quantity
                description=f"{interaction.user.mention} tried to rob {member.mention} and failed\n\n{member.mention} got {rob_quantity} {Constants.COIN} added to his wallet"
                color=discord.Color.dark_red()
        
        self.update_user_wallet(member_id, new_member_wallet_bal) # updating memebr wallet 
        self.update_user_wallet(user_id, new_user_wallet_bal) # updating user wallet
        rob_embed = self.create_embed(interaction, description=description, color=color)
        await interaction.response.send_message(embed=rob_embed)

    @rob.error
    async def rob_error(self, interaction: discord.Interaction, error) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after, 2) # Remaining time in seconds
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            cd_embed = discord.Embed(
                title="**⏰ You are in timeout!**",
                description=f"You can't rob again before `{int(hours)}` hours and `{minutes}` minutes",
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=cd_embed, ephemeral=True)

    @app_commands.command(name='jackbot', description='Spin the wheel and get a chance to win the jackbot prize')
    async def jackbot(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return

        user_id = interaction.user.id

        current_jackbot_prize = SlotMachineService.get_jackbot_prize()

        jackbot_embed = discord.Embed(
            title="**Welcome To Jackbot**",
            description=(
                f"Jackbot is the game of luck, wanna try yours?\n"
                f"Spin the wheel for just a total of **300** {Constants.COIN}\n"
                f"and get a chance to win a Huge amount of {Constants.COIN}\n\n"
                f"```This Message Will auto delete after 5 mins```"
            ),
            color=discord.Color.gold()
        )
        jackbot_embed.add_field(
            name="**Current Prize Pool:**",
            value=f"{current_jackbot_prize:,}"
        )
        jackbot_embed.set_author(icon_url=interaction.guild.icon, name=f"{interaction.guild.name}'s Jackbot")
        jackbot_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)

        spin_btn = Button(
            style=ButtonStyle.primary,
            label="Spin",
            emoji=f"{Constants.SLOT_EMOJI}"
        )

        exit_btn = Button(
            style=ButtonStyle.danger,
            label="Exit",
            emoji="✖"
        )

        jackbot_view = View()
        jackbot_view.add_item(spin_btn)
        jackbot_view.add_item(exit_btn)

        await interaction.response.send_message(embed=jackbot_embed, view=jackbot_view, delete_after=300)

        async def spin_btn_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You can't use other member game", ephemeral=True)
                return

            player_id = interaction.user.id
            player_data = self.get_user_data(player_id)

            if player_data is None:
                await interaction.response.send_message("You don't have bank account use `/balance`", ephemeral=True)
                return
            
            if player_data[2] < 300:
                not_enough = self.create_embed(interaction, description=f"You only have {player_data[2]} {Constants.COIN}, You need 300 {Constants.COIN} to play", color=discord.Color.dark_red())
                await interaction.response.send_message(embed=not_enough, ephemeral=True)
                return
            
            teer1 = choice(Constants.SLOT_TEERS)
            teer2 = choice(Constants.SLOT_TEERS)
            teer3 = choice(Constants.SLOT_TEERS)

            if teer1 == teer2 == teer3:
                new_wallet_balance = player_data[2] + (current_jackbot_prize - 300)
                spin_embed = discord.Embed(
                    title = "**You Won The Jackbot**",
                    description =(
                        f"Today is your lucky day! You have won the grand prize with total of {current_jackbot_prize}\n\n"
                        f"Your wallet now is filled with {new_wallet_balance} {Constants.COIN}\n\n"
                    ),
                    color = discord.Color.gold(),
                    timestamp=datetime.now()
                )
                SlotMachineService.update_jackbot_prize(10000)
                spin_embed.add_field(
                    name="**Machine Stopped on:**",
                    value=f"{teer1}  {teer2}  {teer3}"
                )
                spin_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)
                await interaction.response.edit_message(content=f"@everyone {interaction.user.mention} has just won the prize pool", embed=spin_embed, view=None)
            else:
                new_wallet_balance = player_data[2] - 300
                spin_embed = discord.Embed(
                    title = "**You lost**",
                    description = f"This time you were unlucky and lost 300 {Constants.COIN}\nYou have {new_wallet_balance} {Constants.COIN} in your wallet",
                    color = discord.Color.dark_red(),
                    timestamp=datetime.now()
                )
                SlotMachineService.update_jackbot_prize(current_jackbot_prize + 300)
            
                spin_embed.add_field(
                    name="**Machine Stopped on:**",
                    value=f"{teer1}  {teer2}  {teer3}"
                )
                spin_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)
                self.update_user_wallet(player_id, new_wallet_balance)
                await interaction.response.edit_message(embed=spin_embed, view=None)
            
            logger.info(f"{interaction.user.name} spinned the wheel")

        async def exit_btn_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You can't use other member game", ephemeral=True)
                return
            
            exit_embed = discord.Embed(
                title="**Jackbot game canceled**",
                description="You have canceld the game",
                color=discord.Color.dark_red()
            )
            exit_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)
            
            logger.info(f"{interaction.user.name} Canceld jackbot game!")
            await interaction.response.edit_message(embed=exit_embed, view=None, delete_after=1.5)

        spin_btn.callback = spin_btn_callback
        exit_btn.callback = exit_btn_callback


async def setup(client):
    await client.add_cog(Games(client))
