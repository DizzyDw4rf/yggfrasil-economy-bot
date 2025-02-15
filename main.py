import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')

class MyBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self) -> None:
        await self.tree.sync()
        print(f"Logged in as: {self.user}")
    
    async def load_cogs(self) -> None:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != "__init__.py":
                await self.load_extension(f'cogs.{filename[:-3]}')
    
    async def start_bot(self, token) -> None:
        async with self:
            await self.load_cogs()
            await self.start(token)


client = MyBot(command_prefix='*', intents=discord.Intents.all())

async def main() -> None:
    await client.start_bot(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Going to sleep')
