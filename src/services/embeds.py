import discord
from datetime import datetime


class EmbedService:


    async def send_inv_embed(interaction) -> discord.Embed:
        inv_embed = discord.Embed(
            title='Join our server',
            description=(
            f'You can Use the bot here: '
            f'[𝐘𝐆𝐆𝐃𝐑𝐀𝐒𝐈𝐋🌳](https://discord.gg/KDuf8kvJf4)'
            ),
            color=discord.Color.dark_green()
        )
        await interaction.response.send_message(embed=inv_embed)

    async def send_error_embed(interaction: discord.Interaction, title: str) -> discord.Embed:
        err_embed = discord.Embed(
            title=title,
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=err_embed, ephemeral=True)

    def create_embed(interaction: discord.Interaction, title: str = None, description: str =None, color: discord.Colour = discord.Color.blue()) -> discord.Embed:
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
