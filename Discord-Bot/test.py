import discord
from discord.ext import commands
from dotenv import load_dotenv

# for cogs
import os
import asyncio

intents = discord.Intents.default()

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=intents)

bot.run(token)