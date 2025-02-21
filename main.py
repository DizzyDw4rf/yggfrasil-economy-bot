import discord
import os
import asyncio
import logging
import config
from discord.ext import commands,tasks

from dotenv import load_dotenv
from src.utils.constants import Constants
from paths import COGS_DIR


config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("bot")
load_dotenv()
TOKEN = os.getenv('TOKEN')

class MyBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.activity_name = Constants.BOT_STATUS
        
        self.current_activity_index = 0

    async def on_ready(self) -> None:
        logger.info(f"User: {self.user} - ID: {self.user.id}")
        await self.tree.sync()
        await self.change_activity_name.start()
    
    @tasks.loop(seconds=5)
    async def change_activity_name(self):
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Streaming(
                name=self.activity_name[self.current_activity_index], 
                url="https://twitch.tv/yggdrasill707"))

        self.current_activity_index = (self.current_activity_index + 1) % len(self.activity_name)
    
    @change_activity_name.before_loop
    async def before_change_activity_name(self):
        await self.wait_until_ready()

    async def load_cogs(self) -> None:
        for filename in os.listdir(COGS_DIR):
            if filename.endswith('.py') and filename != "__init__.py":
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Loaded Cog: {filename[:-3]}")
                except Exception as e:
                    logger.error(f"Failed to load Cog: {filename[:-3]}")
                    logger.error(e)
    
    async def start_bot(self, token) -> None:
        async with self:
            await self.load_cogs()
            await self.start(token)


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

client = MyBot(command_prefix='*', intents=intents)


async def main() -> None:
    await client.start_bot(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Going to sleep')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
