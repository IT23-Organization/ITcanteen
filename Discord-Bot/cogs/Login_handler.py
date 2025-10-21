import discord
from discord import activity
from discord.ext import commands

class Login(commands.Cog):
 
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game("Commands To login type : !Login"))
        print(f"{__name__} is Loaded!")

async def setup(bot):
    await bot.add_cog(Login(bot))