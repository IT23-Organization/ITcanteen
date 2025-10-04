import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} ready to go!")

#menu command
@bot.command()
async def menu(ctx):
    await ctx.send(file=discord.File('Discord-Bot/image/menu.jpg'))

# Respond to messages in ticket channels
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.name.startswith("ticket-"):
        if "open ticket" in message.content.lower():
            await message.channel.send(file=discord.File('image/menu.jpg'))
    await bot.process_commands(message)

test_channel = 1419714011812991096

bot.run(token)
