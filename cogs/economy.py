import json
import discord
from discord import app_commands
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, Button
from random import randint
from datetime import datetime
from src.bot_status import BotStatus
from src.utils.tools import formatted_time


bank_file = 'main_bank.json'
BotStatus.set_debug(True)
server = BotStatus.get_server()

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
    
    def get_bank_data(self) -> dict:
        with open(bank_file) as f:
            users = json.load(f)
        return users

    async def open_account(self, interaction) -> discord.Embed:
        users = self.get_bank_data()
        user_id = str(interaction.user.id)
        with open(bank_file, 'w') as f:
            users[user_id] = {}
            users[user_id]['wallet'] = 0
            users[user_id]['bank'] = 1000
            users[user_id]['transactions'] = {}
            users[user_id]['transactions']['last_sand'] = {}
            users[user_id]['transactions']['last_sand']['amount'] = 0
            users[user_id]['transactions']['last_sand']['date'] = 0
            users[user_id]['transactions']['last_recive'] = {}
            users[user_id]['transactions']['last_recive']['amount'] = 0
            users[user_id]['transactions']['last_recive']['date'] = 0
            users[user_id]['inventory'] = {}
            json.dump(users, f, indent=2)
        new_acc = discord.Embed(
            title='New Bank Account',
            description=(
                f'{interaction.user.mention}\'s fresh Bank Account.\n\n'
                f'**Wallet 💰**: {users[user_id]['wallet']} 🍀\n\n'
                f'**Bank 🏛**: {users[user_id]['bank']} 🍀'
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=new_acc)

    @app_commands.command(name='balance', description='Shows the balance of the user opens bank account if user don\'t own one')
    async def balance(self, interaction : discord.Interaction, member: discord.Member = None) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            users = self.get_bank_data()
            user_id = str(interaction.user.id)

            if not member: # If no member Chosen show the user balance
                # Checking if user has an account
                if user_id not in users:
                    # Create a new account
                    await self.open_account(interaction)
                else: # Show the balance of the account
                    exist_acc = discord.Embed(
                        title=f'{interaction.user.display_name}\'s Balance',
                        description=(
                            f'**Wallet 💰**: {users[user_id]['wallet']} 🍀\n\n'
                            f'**Bank 🏛**: {users[user_id]['bank']} 🍀'
                        ),
                        color=discord.Color.green()
                    )
                    await interaction.response.send_message(embed=exist_acc)
            else:
                member_id = str(member.id)
                if member_id not in users: # If member not in user send not found message
                    await interaction.response.send_message('This member don\'t have Balance Account', ephemeral=True)
                else:
                    member_embed = discord.Embed(
                        title=f'{member.display_name}\'s Balance',
                        description=(
                            f'**Wallet 💰**: {users[member_id]['wallet']} 🍀\n\n'
                            f'**Bank 🏛**: {users[member_id]['bank']} 🍀'
                        ),
                        color=discord.Colour.green()
                    )
                    await interaction.response.send_message(embed=member_embed)

    @app_commands.describe(member='A member exists in the guild', amount='The positive number you will to give to user')
    @app_commands.command(name='add', description='Give member Currency')
    async def add(self, interaction: discord.Interaction, member: discord.Member, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            # Checking for adminstrator permission
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('You don\'t have `Adminstrator`', ephemeral=True)
            else:
                member_id = str(member.id)
                users = self.get_bank_data()
                # Validating member has bank account
                if member_id not in users:
                    await interaction.response.send_message(f'{member.display_name}\'s Don\'t have bank account!', ephemeral=True)
                else: # check if amount is valid then add it to bank
                    amount = abs(amount)
                    with open(bank_file, 'w') as f:
                        users[member_id]['bank'] += amount
                        json.dump(users, f, indent=2)
                    added_embed = discord.Embed(
                        title=f'{member.display_name} Has been rewareded with {amount} 🍀',
                        description=f'His **Bank 🏛**:  {users[member_id]['bank']} 🍀',
                        color=discord.Color.yellow()
                    )
                    await interaction.response.send_message(embed=added_embed)
    
    @app_commands.describe(member='A member exists in the guild', amount='The positive number you will to remove from user')
    @app_commands.command(name='remove', description='Remove currency from member')
    async def remove(self, interaction: discord.Interaction, member: discord.Member, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            # Validating adminstrator permission
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('You don\'t have `Adminstrator`', ephemeral=True)
            else:
                member_id = str(member.id)
                users = self.get_bank_data()
                # Validating member has bank account
                if member_id not in users:
                    await interaction.response.send_message(f'{member.display_name}\'s Don\'t have bank account!', ephemeral=True)
                else: 
                    amount = abs(amount)
                    # amount < = total balance
                    if amount <= users[member_id]['bank'] + users[member_id]['wallet']:
                        if amount <= users[member_id]['bank']: # Remove from bank if possible
                            with open(bank_file, 'w') as f:
                                users[member_id]['bank'] -= amount
                                json.dump(users, f, indent=2)
                            rmv_embed = discord.Embed(
                                title=f'{member.display_name} has been punished',
                                description=(
                                    f'His **Bank 🏛**:  {users[member_id]['bank']} 🍀'
                                ),
                                color=discord.Color.red()
                            )
                            await interaction.response.send_message(embed=rmv_embed)
                        else: # Take all from bank and remaining from wallet
                            with open(bank_file, 'w') as f:
                                users[member_id]['wallet'] -= (amount - users[member_id]['bank'])
                                users[member_id]['bank'] = 0
                                json.dump(users, f, indent=2)
                            rmv_embed = discord.Embed(
                                title=f'{member.display_name} has been punished',
                                description=(
                                    f'His **Wallet 💰**: {users[member_id]['wallet']} 🍀\n'
                                    f'His **Bank 🏛**:  0 🍀'
                                ),
                                color=discord.Color.red()
                            )
                            await interaction.response.send_message(embed=rmv_embed)
                    else: # amount > total balance
                        # Remove all in bank and wallet
                        with open(bank_file, 'w') as f:
                            users[member_id]['wallet'] = 0
                            users[member_id]['bank'] = 0
                            json.dump(users, f, indent=2)
                        rmv_embed = discord.Embed(
                                title=f'{member.display_name} has been punished',
                                description=(
                                    f'His **Wallet 💰**: 0 🍀\n'
                                    f'His **Bank 🏛**:  0 🍀'
                                ),
                                color=discord.Color.red()
                            )
                        await interaction.response.send_message(embed=rmv_embed)

    @app_commands.command(name='daily', description='Reward currency to member once every day')
    @app_commands.checks.cooldown(1, 86400, key=lambda i: i.user.id)
    async def daily(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            users = self.get_bank_data()
            user_id = str(interaction.user.id)
            if user_id not in users:
                await interaction.response.send_message('Use `/balance` to open account first.', ephemeral=True)
            else:
                rand_amount = randint(500, 1001)
                with open(bank_file, 'w') as f:
                    users[user_id]['bank'] += rand_amount
                    json.dump(users, f, indent=2)
                daily_embed = discord.Embed(
                    title=f'{interaction.user.display_name} Got a reward.',
                    description=(
                        f'Your **Bank 🏛** increased with {rand_amount} 🍀\n\n'
                        f'**Wallet 💰**: {users[user_id]['wallet']} 🍀\n\n'
                        f'**Bank 🏛**:  {users[user_id]['bank']} 🍀'
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
                title='**⏰ You are in timeout**',
                description=f'You must wait {int(hours)} hours and {int(minutes)} minutes before using this command again.',
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=cd_embed, ephemeral=True)

    @app_commands.describe(member="An member exists in the Guild", amount="The amount of credits you will to give to the member")
    @app_commands.command(name='send', description='Give a user to choose money from your Bank balance')
    async def send(self, interaction: discord.Interaction, member: discord.Member, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            users = self.get_bank_data()
            user_id = str(interaction.user.id)
            member_id = str(member.id)
            if user_id not in users:
                await interaction.response.send_message('Use `/balance` to create bank account\nYou can\'t send credits without an account', ephemeral=True)
            elif member_id not in users:
                await interaction.response.send_message('The member you want to send him credits don\'t have a bank account inform him to use `/balance` to create one!', ephemeral=True)
            else:
                amount = abs(amount)
                send_btn = Button(
                    style= ButtonStyle.blurple,
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
                verify_embed = discord.Embed(
                    title='**Transaction verification**',
                    description=(
                        f'Are you sure you want to send {amount} 🍀 to {member.display_name}?'
                    ),
                    color=discord.Color.blurple()
                )
                await interaction.response.send_message(embed=verify_embed, view=transaction_view)

            async def send_btn_callback(interaction: discord.Interaction) -> None:
                if interaction.user.id == int(user_id):
                    if amount > users[user_id]['bank']:
                        not_enough = discord.Embed(
                            title=f'You tried to send {amount} 🍀',
                            description=f'Your **Bank 🏛**: {users[user_id]['bank']}',
                            color=discord.Color.dark_red()
                        )
                        await interaction.response.send_message(embed=not_enough)
                    else:
                        with open(bank_file, 'w') as f:
                            users[user_id]['bank'] -= amount
                            users[member_id]['bank'] += amount
                            users[user_id]['transactions']['last_sand']['amount'] = amount
                            users[user_id]['transactions']['last_sand']['date'] = Economy.date
                            users[member_id]['transactions']['last_recive']['amount'] = amount
                            users[member_id]['transactions']['last_recive']['date'] = Economy.date
                            json.dump(users, f, indent=2)
                        trans_done = discord.Embed(
                            title='**Transaction Completed 🚀**',
                            description=(
                                f'{interaction.user.display_name} sent {member.display_name} {amount} 🍀'
                            ),
                            color=discord.Color.dark_teal()
                        )
                        await interaction.response.edit_message(embed=trans_done, view=None)
                else:
                    await interaction.response.send_message('You can\'t make a decison', ephemeral=True)
            
            async def cancel_btn_callback(interaction: discord.Interaction) -> None:
                if interaction.user.id == int(user_id):
                    cancel_embed = discord.Embed(
                        title='Transaction Canceld ❌',
                        description=f'{interaction.user.display_name} Canceld the transaction to {member.display_name}',
                        color=discord.Color.dark_red()
                    )
                    await interaction.response.edit_message(embed=cancel_embed, view=None)
                else:
                    await interaction.response.send_message('You can\'t make a decison', ephemeral=True)
            
            send_btn.callback = send_btn_callback
            cancel_send_btn.callback = cancel_btn_callback

    @app_commands.command(name='withdraw', description='Move money from bank to your wallet')
    async def withdraw(self, interaction: discord.Interaction, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            users = self.get_bank_data()
            user_id = str(interaction.user.id)
            if user_id not in users:
                await interaction.response.send_message('You can\'t withdraw from bank without bank account.\nUse `/balance` to create one.', ephemeral=True)
            else:
                amount = abs(amount)
                if amount > users[user_id]['bank']:
                    err_embed = discord.Embed(
                        title='Invalid credit Withdraw',
                        description=(
                            f'Your **Bank 🏛**: {users[user_id]['bank']} 🍀\nYou can\'t withdraw {amount} 🍀'
                        ),
                        color=discord.Color.dark_red()
                    )
                    await interaction.response.send_message(embed=err_embed)
                else:
                    with open(bank_file, 'w') as f:
                        users[user_id]['wallet'] += amount
                        users[user_id]['bank'] -= amount
                        json.dump(users, f, indent=2)
                    wd_embed = discord.Embed(
                        title='Successful Withdrawal ✅',
                        description=(
                            f'Your **Wallet 💰**: {users[user_id]['wallet']} 🍀\n\n'
                            f'Your **Bank 🏛**: {users[user_id]['bank']} 🍀'
                        ),
                        color=discord.Color.green()
                    )
                    await interaction.response.send_message(embed=wd_embed)

    @app_commands.command(name='deposit', description='Move money form wallet to your bank')
    async def deposit(self, interaction: discord.Interaction, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            users = self.get_bank_data()
            user_id = str(interaction.user.id)
            if user_id not in users:
                await interaction.response.send_message('You can\'t deposit to bank without bank account.\nUse `/balance` to create one.', ephemeral=True)
            else:
                amount = abs(amount)
                if amount > users[user_id]['wallet']:
                    err_embed = discord.Embed(
                        title='Invalid credit Deposit',
                        description=(
                            f'Your **Wallet 💰**: {users[user_id]['wallet']} 🍀\nYou can\'t deposit {amount} 🍀'
                        ),
                        color=discord.Color.dark_red()
                    )
                    await interaction.response.send_message(embed=err_embed)
                else:
                    with open(bank_file, 'w') as f:
                        users[user_id]['wallet'] -= amount
                        users[user_id]['bank'] += amount
                        json.dump(users, f, indent=2)
                    wd_embed = discord.Embed(
                        title='Successful Deposit ✅',
                        description=(
                            f'Your **Wallet 💰**: {users[user_id]['wallet']} 🍀\n\n'
                            f'Your **Bank 🏛**: {users[user_id]['bank']} 🍀'
                        ),
                        color=discord.Color.green()
                    )
                    await interaction.response.send_message(embed=wd_embed)

    @app_commands.command(name='leaderboard', description='Show the richest 10 people in the Guild')
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != server:
            await self.send_inv_embed(interaction)
        else:
            users = self.get_bank_data()
            leaderboard_embed = discord.Embed(
                color=discord.Color.green()
            )
            leaderboard = []
            for user_id in users:
                usermention = f'<@{user_id}>'
                total_money = users[user_id]['wallet'] + users[user_id]['bank']
                member = (usermention, total_money)
                leaderboard.append(member)

            sorted_leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)

            leaderboard_text =""
            
            for i, (usermention, total_money) in enumerate(sorted_leaderboard[:10], start=1):
                leaderboard_text += f'{i}. {usermention} - {total_money} 🍀\n'
            
            leaderboard_embed.add_field(
                name='**Top 10 Richest Members**',
                value=leaderboard_text,
                inline=False
            )
            await interaction.response.send_message(embed=leaderboard_embed)


async def setup(client):
    await client.add_cog(Economy(client))
