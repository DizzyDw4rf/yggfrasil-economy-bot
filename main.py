import discord
import os
import asyncio
import logging
import config
from discord.ext import commands
from dotenv import load_dotenv
from paths import COGS_DIR


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("bot")
load_dotenv()
TOKEN = os.getenv('TOKEN')

class MyBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self) -> None:
        await self.tree.sync()
        logger.info(f"User: {self.user} - ID: {self.user.id}")
    
    async def load_cogs(self) -> None:
        for filename in os.listdir(COGS_DIR):
            if filename.endswith('.py') and filename != "__init__.py":
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Loaded Cog: {filename[:-3]}")
                except Exception as e:
                    logger.error(f"Failed to load Cog: {filename[:-3]}")
    
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
        logger.info('Going to sleep')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
