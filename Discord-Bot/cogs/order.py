import discord
from discord.ext import commands
import os
import re

# --- ดึงมาจากโค้ดไฟล์ที่ 2 ---
RESTAURANT_MENUS = {
    "mama": "image/menu.jpg",
    "pizza": "image/menu.jpg",
    "kfc": "image/menu.jpg",
    "starbucks": "image/menu.jpg",
    "mcd": "image/menu.jpg",
}

# --- ดึงมาจากโค้ดไฟล์ที่ 1 ---
def parse_menu_item(text):
    pattern = r"(.*?)\s*\((.*?)\)$"
    match = re.search(pattern, text)
    
    if match:
        menu_name = match.group(1).strip()
        note = match.group(2).strip()
        return menu_name, note
    else:
        menu_name = text.strip()
        return menu_name, None

class Ticket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # --- รวม Logic การฟังสรุปไว้ในที่เดียว ---
        if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-"):
            content = message.content.strip()
            lower = content.lower()

            # 1. เช็ก "open ticket" (จากทั้งสองไฟล์)
            if "open ticket" in lower:
                await message.channel.send(
                    "These are the restaurants in the canteen:\n1. Mama\n2. Pizza\n3. KFC\n4. Starbucks\n5. McD\nType `!menu <name>` to see the menu. eg `!menu mama`"
                )
                return
            
            # 2. เช็กออเดอร์ (จากไฟล์ที่ 1)
            if not content.startswith("!"): 
                menu, note = parse_menu_item(content)

                embed = discord.Embed(
                    title="[S]บันทึกออเดอร์ (WIP) :tropical_drink:",
                    description="ร้านอาหารได้รับออเดอร์ของคุณ และกำลังเตรียมอาหารให้สำหรับคุณ",
                    color=discord.Color.green()
                )
                
                embed.add_field(name="ชื่อเมนู", value=menu, inline=False)
                
                if note:
                    embed.add_field(name="หมายเหตุเพิ่มเติม (สำหรับลูกค้า)", value=note, inline=False)
                else:
                    embed.add_field(name="หมายเหตุเพิ่มเติม (สำหรับลูกค้า)", value="ไม่มี", inline=False)
                    
                embed.set_footer(text=f"รับเรื่องโดย: {message.author.name}")

                await message.channel.send(embed=embed)
                await message.channel.send("รับออเดอร์แล้ว")
                return

        # 3. ถ้าไม่ใช่ทั้งสองอย่าง ให้ส่งไปประมวลผลคำสั่ง (เช่น !menu)
        await self.bot.process_commands(message)

    # --- ดึงมาจากโค้ดไฟล์ที่ 2 ---
    @commands.command(name="menu")
    async def menu_cmd(self, ctx: commands.Context, restaurant: str = None):
        if restaurant is None:
            await ctx.send("Please specify a restaurant. Example: `!menu mama`")
            return
        rest = restaurant.lower()
        path = RESTAURANT_MENUS.get(rest)
        if path and os.path.isfile(path):
            await ctx.send(file=discord.File(path))
        else:
            await ctx.send("Sorry, I don't have the menu for that restaurant.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ticket(bot))
