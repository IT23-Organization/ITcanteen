import discord
from discord import activity
from discord.ext import commands

class test(commands.Cog):
 
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def On_ready(self):
        await self.bot.change_presence(activity=discord.Game("Im online!"))
        print("Im online")

def SetUp(bot):
    bot.add_cog(test(bot))