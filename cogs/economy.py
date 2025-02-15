import json
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv



bank_file = 'main_bank.json'
load_dotenv()
ALLOWED_GUILD_ID = os.getenv('ALLOWED_GUILD_ID')

class Economy(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    def get_bank_data(self) -> dict:
        with open('main_bank.json') as f:
            users = json.load(f)
        return users
    
    async def open_account(self, interaction) -> discord.Embed:
        users = self.get_bank_data()
        user_id = str(interaction.user.id)
        with open(bank_file, 'w') as f:
            users[user_id] = {}
            users[user_id]['wallet'] = 0
            users[user_id]['bank'] = 0
            json.dump(users, f, indent=2)
        new_acc = discord.Embed(
            title='New Bank Account',
            description=(
                f'{interaction.user.mention}\'s fresh Bank Account.\n\n'
                f'Wallet 💰: {users[user_id]['wallet']}\t\t\t\t\t\t'
                f'Bank 🏛: {users[user_id]['bank']}'
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=new_acc)

    @app_commands.command(name='balance', description='Shows the balance of the user opens bank account if user don\'t own one')
    async def balance(self, interaction : discord.Interaction) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != ALLOWED_GUILD_ID:
            inv_embed = discord.Embed(
                title='To use this bot please Join our server',
                description='https://discord.gg/KDuf8kvJf4'
            )
            await interaction.response.send_message(embed=inv_embed)
        else:
            users = self.get_bank_data()
            user_id = str(interaction.user.id)
            # Checking if user has an account
            if user_id not in users:
                # Create a new account
                await self.open_account(interaction)
            else: # Show the balance of the account
                exist_acc = discord.Embed(
                    title=f'{interaction.user.mention}\'s Balance',
                    description=(
                        f'Wallet 💰: {users[user_id]['wallet']}\t\t\t\t\t\t'
                        f'Bank 🏛: {users[user_id]['bank']}'
                    ),
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=exist_acc)

    @app_commands.describe(member='A member exists in the guild', amount='The positive number you will to give to user')
    @app_commands.command(name='add', description='Give member Currency')
    async def add(self, interaction: discord.Interaction, member: discord.Member, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != ALLOWED_GUILD_ID:
            inv_embed = discord.Embed(
                title='To use this bot please Join our server',
                description='https://discord.gg/KDuf8kvJf4'
            )
            await interaction.response.send_message(embed=inv_embed)
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
                        title=f'{member.mention} Has been rewareded',
                        description=f'His balance increased with {amount} 💵',
                        color=discord.Color.yellow()
                    )
                    await interaction.response.send_message(embed=added_embed)
    
    @app_commands.command(name='remove', description='Remove currency from member')
    async def remove(self, interaction: discord.Interaction, member: discord.Member, amount: int = 100) -> None:
        if str(interaction.guild) and str(interaction.guild_id) != ALLOWED_GUILD_ID:
            inv_embed = discord.Embed(
                title='To use this bot please Join our server',
                description='https://discord.gg/KDuf8kvJf4'
            )
            await interaction.response.send_message(embed=inv_embed)
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
                else: # check if amount is valid and amount < bank else bank = 0
                    amount = abs(amount)
                    if amount > users[member_id]['bank']:
                        with open(bank_file, 'w') as f:
                            users[member_id]['bank'] = 0
                            json.dump(users, f, indent=2)
                        rmv_embed = discord.Embed(
                            title=f'{member.mention} has been punished',
                            description=f'His bank balance returned to 0 💵',
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=rmv_embed)
                    else: # remove the amount from bank
                        with open(bank_file, 'w') as f:
                            users[member_id]['bank'] -= amount
                            json.dump(users, f, indent=2)
                        rmv_embed = discord.Embed(
                            title=f'{member.mention} has been punished',
                            description=f'His bank balance decreased with {amount} 💵',
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=rmv_embed)


async def setup(client):
    await client.add_cog(Economy(client))
