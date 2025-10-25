import discord
from discord import activity
from discord.ext import commands
from discord import app_commands

GUILD_ID = 1418981762872115343

class Login(commands.Cog):
 
    def __init__(self, bot):
        self.bot = bot
        self._synced = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game("login type : !Login"))
        if not self.bot.synced: 
            try:
                # The crucial part: Call .sync() on the bot's central command tree
                
                # --- OPTION A: GUILD SYNC (Fastest for testing) ---
                test_guild = discord.Object(id=GUILD_ID)
                synced = await self.bot.tree.sync(guild=test_guild)
                print(f"SyncCog: Synced {len(synced)} commands to guild {GUILD_ID}.")
                
                # --- OPTION B: GLOBAL SYNC (Slow, for production) ---
                # synced = await self.bot.tree.sync()
                # print(f"SyncCog: Globally synced {len(synced)} commands.")
                
                self.bot.synced = True # Set the flag to prevent re-syncing
                
            except Exception as e:
                print(f"SyncCog: Failed to sync commands: {e}")
        print(f"{__name__} is Loaded!")
    @commands.command(name="login")
    async def login(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}, you trigger the !login command!")
    
    @app_commands.command(name="secret", description="Sends an ephemeral message.")
    async def secret_command(self, interaction: discord.Interaction):
        # The key is the 'ephemeral=True' argument
        await interaction.response.send_message("Shhh! This message is only for your eyes 👀.", ephemeral=True)
        # You must use interaction.response for the initial response.
async def setup(bot):
    bot.synced = False
    await bot.add_cog(Login(bot))