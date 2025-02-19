import discord
import config
import logging
from discord import app_commands
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, Button
from random import randint
from datetime import datetime
from src.bot_status import BotStatus
from src.utils.tools import formatted_time, remove_tax
from src.utils.constants import Constants
from src.services.databases import DatabaseService
from src.services.tax import TaxService


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("discord")

BotStatus.set_debug(False)
server = BotStatus.get_server()

DatabaseService.create_user_table()
DatabaseService.create_transaction_table()

class Economy(commands.Cog):
    
    date = formatted_time(str(datetime.now()))
    
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
    
    def create_embed(self,interaction: discord.Interaction, title: str, description: str, color: discord.Colour) -> discord.Embed:
        """
        This function create an Embed message with footer showing date and user name and icon
        """
        user = interaction.user.name
        icon = interaction.user.display_avatar
        em = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        em.set_footer(text=f'Used by: {user}', icon_url=icon)
        return em
    
    def get_user_data(self, user_id: int):
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT * FROM Users WHERE id = ?""", (user_id,))
            return c.fetchone()
    
    def create_user(self, user_id: int, username: str) -> None:
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO Users (id, username) VALUES (?, ?)""", (user_id, username))
            conn.commit()
    
    def update_user(self, user_id: int, wallet: int, bank: int) -> None:
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""UPDATE Users SET wallet = ?, bank = ? WHERE id = ?""", (wallet, bank, user_id))
            conn.commit()

    async def open_account(self, interaction) -> discord.Embed:
        user_id = interaction.user.id
        username = interaction.user.display_name
        self.create_user(user_id=user_id, username=username)
        new_acc = discord.Embed(
            title='New Bank Account',
            description=(
                f'{interaction.user.mention}\'s fresh Bank Account.\n\n'
                f'{Constants.WALLET}: 500 {Constants.COIN}\n\n'
                f'{Constants.BANK}: 500 {Constants.COIN}\n\n'
                f'**Total**: 1000 {Constants.COIN}'
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=new_acc)

    @app_commands.command(name='balance', description='Shows the balance of the user opens bank account if user don\'t own one')
    async def balance(self, interaction : discord.Interaction, member: discord.Member = None) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        user_id = interaction.user.id
        user_data = self.get_user_data(user_id=user_id)
        
        if not member: # If no member Chosen show the user balance
            # Checking if user has an account
            if user_data is None:
                # Create a new account
                await self.open_account(interaction)
                return
            # Show the balance of the account
            username, wallet, bank =user_data[1], user_data[2], user_data[3]
            title=f'{username}\'s Balance'
            description=(
                f'{Constants.WALLET}: {wallet} {Constants.COIN}\n\n'
                f'{Constants.BANK}: {bank} {Constants.COIN}\n\n'
                f'**Total**: {bank + wallet} {Constants.COIN}'
            )
            color=discord.Color.green()

        else:
            member_id = member.id
            member_data = self.get_user_data(member_id)
            if member_data is None: # If member not in user send not found message
                await interaction.response.send_message('This member don\'t have Balance Account', ephemeral=True)
                return
            
            username, wallet, bank = member_data[1], member_data[2], member_data[3]
            title=f'{username}\'s Balance'
            description=(
                f'{Constants.WALLET}: {wallet} {Constants.COIN}\n\n'
                f'{Constants.BANK}: {bank} {Constants.COIN}\n\n'
                f'**Total**: {bank + wallet} {Constants.COIN}'
            )
            color=discord.Colour.green()
            
        bal_embed = self.create_embed(interaction, title=title, description=description, color=color)
        await interaction.response.send_message(embed=bal_embed)

    @app_commands.describe(member='A member exists in the guild', amount='The positive number you will to give to user')
    @app_commands.command(name='add', description='Give member Currency')
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
        else:
            member_id = member.id
            member_data = self.get_user_data(member_id)
            # Validating member has bank account
            if member_data is None:
                await interaction.response.send_message(f'{member.display_name}\'s Don\'t have bank account!', ephemeral=True)
                return
            # check if amount is valid then add it to bank
            new_bank_balance = member_data[3] + abs(amount)
            self.update_user(member_id, member_data[2], new_bank_balance)
            added_embed = self.create_embed(
                interaction,
                title=f'{member.display_name} Has been rewareded with {amount} {Constants.COIN}',
                description=f'His {Constants.BANK}:  {new_bank_balance} {Constants.COIN}',
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=added_embed)
    
    @add.error
    async def add_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            em = discord.Embed(
                description=f"{interaction.user.mention} You have to be an Adminstrator to use this Command.",
                color=discord.Color.dark_red()
            )
            logger.error(f"{interaction.user.name} Tried to use /add command while he not adminstartor")
            await interaction.response.send_message(embed=em, ephemeral=True)

    @app_commands.describe(member='A member exists in the guild', amount='The positive number you will to remove from user')
    @app_commands.command(name='remove', description='Remove currency from member')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
        else:
            member_id = member.id
            member_data = self.get_user_data(member_id)
            # Validating member has bank account
            if member_data is None:
                await interaction.response.send_message(f'{member.display_name}\'s Don\'t have bank account!', ephemeral=True)
                return
            # amount < = total balance
            wallet, bank = member_data[2], member_data[3]
            total_balance = wallet + bank
            if amount <= total_balance:
                if amount <= bank: # Remove from bank if possible
                    new_bank_balance = bank - amount
                    self.update_user(member_id, wallet, new_bank_balance)
                    rmv_embed = self.create_embed(
                        interaction,
                        title=f'{member.display_name} has been punished',
                        description=(
                            f'His {Constants.BANK}:  {new_bank_balance} {Constants.COIN}'
                        ),
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=rmv_embed)
                else: # Take all from bank and remaining from wallet
                    new_wallet_balance = wallet - (amount - bank)
                    self.update_user(member_id, new_wallet_balance, 0)
                    rmv_embed = self.create_embed(
                        interaction,
                        title=f'{member.display_name} has been punished',
                        description=(
                            f'His {Constants.WALLET}: {new_wallet_balance} {Constants.COIN}\n'
                            f'His {Constants.BANK}:  0 {Constants.COIN}'
                        ),
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=rmv_embed)
            else: # amount > total balance
                # Remove all in bank and wallet
                self.update_user(member_id, 0, 0)
                rmv_embed = self.create_embed(
                    interaction,
                        title=f'{member.display_name} has been punished',
                        description=(
                            f'His {Constants.WALLET}: 0 {Constants.COIN}\n'
                            f'His {Constants.BANK}:  0 {Constants.COIN}'
                        ),
                        color=discord.Color.red()
                    )
                await interaction.response.send_message(embed=rmv_embed)

    @remove.error
    async def remove_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            em = discord.Embed(
                description=f"{interaction.user.mention} You have to be an Adminstrator to use this Command.",
                color=discord.Color.dark_red()
            )
            logger.error(f"{interaction.user.name} Tried to use /remove command while he not adminstartor")
            await interaction.response.send_message(embed=em, ephemeral=True)

    @app_commands.command(name='daily', description='Reward currency to member once every day')
    @app_commands.checks.cooldown(1, 86400, key=lambda i: i.user.id)
    async def daily(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
        else:
            user_id = interaction.user.id
            user_data = self.get_user_data(user_id)
            if user_data is None:
                await interaction.response.send_message('Use `/balance` to open account first.', ephemeral=True)
                return
            
            rand_amount = randint(500, 1000)
            username, wallet , bank = user_data[1], user_data[2], user_data[3]
            new_bank_balance = bank + rand_amount
            self.update_user(user_id, wallet, new_bank_balance)
            daily_embed = self.create_embed(
                interaction,
                title=f'{username} Got a reward.',
                description=(
                    f'Your {Constants.BANK} increased with {rand_amount} {Constants.COIN}\n\n'
                    f'{Constants.WALLET}: {wallet} {Constants.COIN}\n\n'
                    f'{Constants.BANK}:  {new_bank_balance} {Constants.COIN}\n\n'
                    f'**Total**: {wallet + new_bank_balance}'
                ),
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=daily_embed)

    # Error handling for daily cooldown
    @daily.error
    async def daily_error(self, interaction: discord.Interaction, error) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after, 2) # time remaining in seconds
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            cd_embed = discord.Embed(
                title='**⏰ You are in timeout!**',
                description=f'You must wait `{int(hours)}` hours and `{minutes}` minutes before using this command again.',
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=cd_embed, ephemeral=True)

    @app_commands.describe(member="An member exists in the Guild", amount="The amount of credits you will to give to the member")
    @app_commands.command(name='send', description='Give a user to choose money from your Bank balance')
    async def send(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 100]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        user_id = interaction.user.id
        member_id = member.id
        if user_id == member_id:
            logger.info(f"{interaction.user.name} Tried to send himself credits")
            await interaction.response.send_message("You can't send yourself credits", ephemeral=True)
            return
        user_data = self.get_user_data(user_id)
        member_data = self.get_user_data(member_id)
        if user_data is None or member_data is None:
            await interaction.response.send_message('User Not Found in bank account.\nMake sure to use"/balance" to create account', ephemeral=True)
            return

        taxed_amount = remove_tax(amount=amount, tax_rate=TaxService.get_tax_rate()) # Calculating amount after taking Taxes

        send_btn = Button(
            style= ButtonStyle.primary,
            label='Send',
            emoji='🚀'
        )
        cancel_send_btn = Button(
            style= ButtonStyle.danger,
            label='Cancel',
            emoji='✖'
        )
        
        transaction_view = View()
        transaction_view.add_item(send_btn)
        transaction_view.add_item(cancel_send_btn)
        verify_embed = self.create_embed(
            interaction,
            title='**Transaction verification**',
            description=(
                f'Are you sure you want to send {amount} {Constants.COIN} to {member.display_name}?\n\n'
                f"```This message will be deleted after 5 mins if no action taken.```"
            ),
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=verify_embed, view=transaction_view, delete_after=300)

        async def send_btn_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id == int(user_id):
                if amount > user_data[3]:
                    not_enough = self.create_embed(
                        interaction,
                        title=f'You tried to send {amount} {Constants.COIN}',
                        description=f'Your {Constants.BANK}: {user_data[3]}',
                        color=discord.Color.dark_red()
                    )
                    await interaction.response.edit_message(embed=not_enough, view=None)
                else:
                    new_sender_bank_balance = user_data[3] - amount
                    new_receiver_bank_balance = member_data[3] + taxed_amount
                    
                    # Update Sender bank balance 
                    self.update_user(user_id, user_data[2], new_sender_bank_balance)

                    # Update receiver bank balance
                    self.update_user(member_id, member_data[2], new_receiver_bank_balance)

                    # Inserting Transaction record 
                    with DatabaseService.db_connection() as conn:
                        c = conn.cursor()
                        # Send transaction record
                        c.execute(
                            """INSERT INTO Transactions (UserId, Amount, TransactionDate, TransactionType) VALUES (?, ?, ?, ?)""",
                            (user_id, amount, Economy.date, 'send')
                        )

                        # Receive transaction record
                        c.execute(
                            """INSERT INTO Transactions (UserId, Amount, TransactionDate, TransactionType) VALUES (?, ?, ?, ?)""",
                            (member_id, amount, Economy.date, 'receive')
                        )
                        conn.commit()

                    trans_done = self.create_embed(
                        interaction,
                        title='**Transaction Completed 🚀**',
                        description=(
                            f'{interaction.user.display_name} sent {member.display_name} {amount} {Constants.COIN}\n\n'
                            f'```{member.name} received {taxed_amount} after taking taxes```'
                        ),
                        color=discord.Color.dark_teal()
                    )
                    logger.info(f"{interaction.user.name} sent {amount} credits to {member.name} on {formatted_time(str(datetime.now()))}")
                    await interaction.response.edit_message(embed=trans_done, view=None)
            else:
                await interaction.response.send_message('You can\'t make a decison', ephemeral=True)
        
        async def cancel_btn_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id == int(user_id):
                cancel_embed = self.create_embed(
                    interaction,
                    title='Transaction Canceld ❌',
                    description=f'{interaction.user.display_name} Canceld the transaction to {member.display_name}',
                    color=discord.Color.dark_red()
                )
                await interaction.response.edit_message(embed=cancel_embed, view=None, delete_after=1.5)
            else:
                await interaction.response.send_message('You can\'t make a decison', ephemeral=True)
        
        send_btn.callback = send_btn_callback
        cancel_send_btn.callback = cancel_btn_callback

    @app_commands.command(name='withdraw', description='Move money from bank to your wallet')
    async def withdraw(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
        else:
            user_id = interaction.user.id
            user_data = self.get_user_data(user_id)
            if user_data is None:
                await interaction.response.send_message('You can\'t withdraw from bank without bank account.\nUse `/balance` to create one.', ephemeral=True)
                return

            taxed_amount = remove_tax(amount=amount, tax_rate=TaxService.get_tax_rate())

            if amount > user_data[3]:
                err_embed = self.create_embed(
                    interaction,
                    title='Invalid credit Withdraw',
                    description=(
                        f'Your {Constants.BANK}: {user_data[3]} {Constants.COIN}\nYou can\'t withdraw {amount} {Constants.COIN}'
                    ),
                    color=discord.Color.dark_red()
                )
                await interaction.response.send_message(embed=err_embed)
            else:
                new_wallet_balance = user_data[2] + taxed_amount
                new_bank_balance = user_data[3] - amount
                self.update_user(user_id, new_wallet_balance, new_bank_balance)
                wd_embed = self.create_embed(
                    interaction,
                    title='Successful Withdrawal ✅',
                    description=(
                        f'Your {Constants.WALLET}: {new_wallet_balance} {Constants.COIN}\n\n'
                        f'Your {Constants.BANK}: {new_bank_balance} {Constants.COIN}\n\n'
                        f'```You received {taxed_amount} after taking taxes```'
                    ),
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=wd_embed)

    @app_commands.command(name='deposit', description='Move money form wallet to your bank')
    async def deposit(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
        else:
            user_id = interaction.user.id
            user_data = self.get_user_data(user_id)
            if user_data is None:
                await interaction.response.send_message('You can\'t deposit to bank without bank account.\nUse `/balance` to create one.', ephemeral=True)
                return
            
            taxed_amount = remove_tax(amount=amount, tax_rate=TaxService.get_tax_rate())

            if amount > user_data[2]:
                err_embed = self.create_embed(
                    interaction,
                    title='Invalid credit Deposit',
                    description=(
                        f'Your {Constants.WALLET}: {user_data[2]} {Constants.COIN}\nYou can\'t deposit {amount} {Constants.COIN}'
                    ),
                    color=discord.Color.dark_red()
                )
                await interaction.response.send_message(embed=err_embed)
            else:
                new_wallet_balance = user_data[2] - amount
                new_bank_balance = user_data[3] + taxed_amount
                self.update_user(user_id, new_wallet_balance, new_bank_balance)
                wd_embed = self.create_embed(
                    interaction,
                    title='Successful Deposit ✅',
                    description=(
                        f'Your {Constants.WALLET}: {new_wallet_balance} {Constants.COIN}\n\n'
                        f'Your {Constants.BANK}: {new_bank_balance} {Constants.COIN}\n\n'
                        f'```Your bank receive {taxed_amount} after taking taxes```'
                    ),
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=wd_embed)

    @app_commands.command(name='leaderboard', description='Show the richest 10 people in the Guild')
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        with DatabaseService.db_connection() as conn:
            c = conn.cursor()
            c.execute("""SELECT id, wallet, bank FROM Users""")
            users = c.fetchall()
        
        leaderboard_embed = discord.Embed(
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        leaderboard_embed.set_author(name="📃 Server Balance Leaderboard", icon_url=interaction.guild.icon)
        leaderboard = []

        for user in users:
            usermention = f'<@{user[0]}>'
            total_money = user[1] + user[2]
            member = (usermention, total_money)
            leaderboard.append(member)

        sorted_leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)

        leaderboard_text =""
        
        for i, (usermention, total_money) in enumerate(sorted_leaderboard[:10], start=1):
            leaderboard_text += f'{i}. {usermention} - {total_money} {Constants.COIN}\n'
        
        leaderboard_embed.add_field(
            name='**Top 10 Richest Members**',
            value=leaderboard_text,
            inline=False
        )
        leaderboard_embed.set_footer(text=f"Used by: {interaction.user.name}", icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=leaderboard_embed)

    @app_commands.command(name='gettax', description="Show the current tax rate of the economy system")
    async def gettax(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        tax_rate = TaxService.get_tax_rate()

        tax_embed = self.create_embed(
            interaction,
            title="**Current Tax Rate**",
            description=f"Tax rate is set at : {tax_rate * 100}%",
            color=discord.Colour.dark_blue()
        )

        await interaction.response.send_message(embed=tax_embed)

    @app_commands.command(name='settax', description="Change the tax rate of the server")
    @app_commands.checks.has_permissions(administrator=True)
    async def settax(self, interaction: discord.Interaction, tax_rate: app_commands.Range[float, 0.0, 5.0]) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            logger.info(f"{interaction.user.name} Tried to use {interaction.command.name} in {interaction.guild.id}")
            await self.send_inv_embed(interaction)
            return
        
        old_tax_rate = TaxService.get_tax_rate()

        user_id = interaction.user.id
        settax_embed = self.create_embed(
            interaction,
            title="**Setting Tax Rate**",
            description=(
                f"Are you sure you want to change tax from {old_tax_rate} to {tax_rate} ?\n\n"
                f"This will affect all server's economy system, Press confirm to procced or Cancel to abort\n\n"
                f"```This message will be deleted after 5 mins if no action taken.```"
            ),
            color=discord.Color.dark_blue()
        )

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

        settax_view = View()
        settax_view.add_item(confirm_btn)
        settax_view.add_item(cancel_btn)

        await interaction.response.send_message(embed=settax_embed, view=settax_view, delete_after=300)
        
        async def confirm_btn_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not the command user!", ephemeral=True)
                return
            
            confirm_embed = self.create_embed(
                interaction,
                title="**Setting Tax Rate**",
                description=f"Tax rate has changed from {old_tax_rate} to {tax_rate}",
                color=discord.Colour.green()
            )
            
            TaxService.update_new_tax_rate(tax_rate)

            logger.info(f"{interaction.user.name} Changed the tax rate to {tax_rate}")
            await interaction.response.edit_message(embed=confirm_embed, view=None, delete_after=1.5)

        async def cancel_btn_callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not the command user!", ephemeral=True)
                return

            cancel_embed = self.create_embed(
                interaction,
                title="**Setting Tax Rate**",
                description=f"Changing tax rate Canceld.",
                color=discord.Color.green()
            )

            logger.info(f"{interaction.user.name} canceld tax rate change")
            await interaction.response.edit_message(embed=cancel_embed, view=None, delete_after=1.5)
        
        confirm_btn.callback = confirm_btn_callback
        cancel_btn.callback = cancel_btn_callback
    
    @settax.error
    async def settax_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            em = discord.Embed(
                description=f"{interaction.user.mention} You have to be an Adminstrator to use this Command.",
                color=discord.Color.dark_red()
            )
            logger.error(f"{interaction.user.name} Tried to use /settax command while he not adminstartor")
            await interaction.response.send_message(embed=em, ephemeral=True)


async def setup(client):
    await client.add_cog(Economy(client))
