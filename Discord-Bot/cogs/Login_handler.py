import discord
from discord import activity
from discord.ext import commands
from discord import app_commands

GUILD_ID = 1418981762872115343
VERIFIED_ROLE_ID = 1433761427767951473
TMPDATA = {
    "68070063" : "ธรรมธัช ก้อนนาค",
    "68070036" : "เอยอิ่มอร่อย เก",
    "68070070" : "ธีรพล อักษรหรั่ง",
}

class Login(commands.Cog):
 
    def __init__(self, bot):
        self.bot = bot
        self._synced = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        # Update the bot's presence to reflect the slash command usage
        await self.bot.change_presence(activity=discord.Game("verify using /verify"))
        
        # Check the cog's internal flag for syncing
        if not self._synced: 
            try:
                # The crucial part: Call .sync() on the bot's central command tree
                
                # --- OPTION A: GUILD SYNC (Fastest for testing) ---
                # Itcanteen = discord.Object(id=GUILD_ID)
                # synced = await self.bot.tree.sync(guild=Itcanteen)
                # print(f"SyncCog: Synced {len(synced)} commands to guild {GUILD_ID}.")
                
                # --- OPTION B: GLOBAL SYNC (Slow, for production) ---
                synced = await self.bot.tree.sync()
                print(f"SyncCog: Globally synced {len(synced)} commands.")
                
                # Set the cog flag to prevent re-syncing on subsequent reloads
                self._synced = True 
                
            except Exception as e:
                print(f"SyncCog: Failed to sync commands: {e}")
        print(f"{__name__} is Loaded!")

    @commands.command(name="login")
    async def login(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}, you trigger the !login command!")

    @app_commands.command(name="secure",description="Give you secure message")
    async def secure_message(self,interaction = discord.Interaction):
        await interaction.response.send_message(
            "This is for you.",
            ephemeral=True
        )

    async def assign_verified_role(self,member: discord.Member,guild : discord.Guild,student_id:str,student_name:str) -> str:
        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        role_status = ""

        if not verified_role:
            role_status = f"Role Not Found: Could not find the role with ID `{VERIFIED_ROLE_ID}`."
        elif verified_role in member.roles:
            role_status = f"Role Already Assigned: Member already has the '{verified_role.name}' role."
        else:
            try:
                await member.add_roles(verified_role)
                role_status = f"Role Assigned: `{verified_role.name}`."
            except discord.Forbidden:
                role_status = "Role assignment failed: Bot lacks permissions/hierarchy."
            except Exception as e:
                role_status = f"Role assignment failed: Error: {e}"
        nick_status = ''
        try:
            fullnick = student_id + "|" + student_name
            if member.nick != fullnick:
                await member.edit(nick=fullnick)
                nick_status = f"Nickname changed to {fullnick}."
            else:
                nick_status = f"Nickname already set to {fullnick}."
        except discord.Forbidden:
            nick_status = "Nickname assign failed : bot lacks permissions/hierarchy."
        except Exception as e:
            nick_status = f"Nickname assignment failed : Error: {e}"
        return f"\n**Verification Status** : {role_status} - {nick_status}"

    @app_commands.command(name ="verify",description="verify by Student ID")
    @app_commands.describe(
        student_id = "Your unique student id (IT faculty only!)"
    )
    async def verifyCommand(self, interaction: discord.Interaction, student_id: str):
        if not student_id or len(student_id) < 8:
            return await interaction.response.send_message(
                "**Error!**\nPlease input a Unique KMITL Student ID.",ephemeral=False)
        await interaction.response.defer(ephemeral=True)

        print("Starting verification process...")

        is_verified = self.isIT(student_id) and self.getName(student_id) is not None
        student_name = self.getName(student_id).split(' ')[0]

        print(f"Verification attempt for ID: {student_id}, Verified: {is_verified}")

        if is_verified:
            base_message = (
                f"✅ **Verification Successful!**\n"
                # f"Student ID `{student_id}` confirmed for IT Faculty (Code 07).\n"
            )
            if interaction.guild and isinstance(interaction.user, discord.Member):
                role_status_message = await self.assign_verified_role(
                    member=interaction.user,
                    guild=interaction.guild,
                    student_id=student_id,
                    student_name=student_name)
            else:
                role_status_message = "\n*Role assignment skipped: Command not run in a guild context.*"
            response_message = f"{base_message}{role_status_message}"
        else:
            response_message = (
                f"❌ **Verification Failed!**\n"
                # f"Student ID `{student_id}` is not recognized as IT Faculty (Code 07)."
            )

        await interaction.followup.send(
            response_message,
            ephemeral=True
        )
    def isIT(self,ID) -> bool:
        try:
            # Extracts digits 3 & 4 (index 2 and 3) and checks if the integer value is 7
            faculty_code = int(ID[2:4])
            is_it = faculty_code == 7
            # The unique ID part is unnecessary for the check, but we keep the logic clean
            # uniqueID = int(student_id[4:])
            return is_it
        except (ValueError, IndexError):
            # If the slicing fails (IndexError) or conversion fails (ValueError),
            # the ID is invalid, so we return False.
            return False
    def getName(self,ID) -> str:
        # แบบไม่ดึงจาก database
        if ID not in TMPDATA:
            return None
        return TMPDATA[ID]
        # แบบดึงจาก database
async def setup(bot):
    bot.synced = False
    await bot.add_cog(Login(bot))