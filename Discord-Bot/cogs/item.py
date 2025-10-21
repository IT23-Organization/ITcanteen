import discord
from discord.ext import commands

class testCommand(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is Loaded!")
    
    @commands.command()
    async def ping(self,ctx):
        ping_embed = discord.Embed(title="Ping", description="Latency in ms",color=discord.Color.blue())
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency(ms): ",value =f"{round(self.bot.latency * 1000)}ms.",inline=False)
        ping_embed.set_footer(text=f"request by {ctx.author.name}.",icon_url=ctx.author.avatar)
        await ctx.send(embed=ping_embed)

async def setup(bot):
    await bot.add_cog(testCommand(bot))