import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

# for cogs
import os
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# cogs loader
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

# bot.run(token,log_handler=handler,log_level=logging.DEBUG)
asyncio.run(main())