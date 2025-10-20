import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?')

#Channel
test_channel = 1419714011812991096

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    clientName = ''
    for i in str(bot.user):
        if i.isalpha():
            clientName += i
    channel = checkChannel(test_channel)
    print(f'Send a message to {channel}')
    if channel:
        await channel.send(f'Hello motherfucker {clientName} is online!')
    else:
        print('channel is not found!')

def checkChannel(ch):
    channel = bot.get_channel(ch)
    if channel:
        return channel
    return 
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

def isMember(member):
    # member gonna have 1:student id | 2:student name
    member.split('|')
    if isStudentID(member[0]):
        if isStudentName(member[1]):
            return True
    return False

def isStudentID(id):
    if id in {}:
        return True
    return False

def isStudentName(name):
    if name in {}:
        return True
    return False

@bot.command()
async def Register(ctx):
    channel = checkChannel()
    if channel:
        await channel.send(f'Hello using register function')
    else:
        print('something went wrong')

bot.run(token,log_handler=handler,log_leveld=logging.DEBUG)