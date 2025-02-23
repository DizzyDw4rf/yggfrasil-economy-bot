import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class Ping(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name='ping', description='Shows bot\'s latency')
    async def ping(self, interaction: discord.Interaction) -> None:
        bot_latency = round(self.client.latency * 1000)
        ping_embed = discord.Embed(
            title="Pong! 🏓",
            description=f"**⌛ Time:** {bot_latency}ms",
            color=discord.Color.brand_green(),
            timestamp=datetime.now()
        )
        ping_embed.set_footer(text=f"Requested by :{interaction.user.name}", icon_url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=ping_embed)


async def setup(client):
    await client.add_cog(Ping(client))
