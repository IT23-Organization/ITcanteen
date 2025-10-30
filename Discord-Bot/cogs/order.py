import discord
from discord.ext import commands
import os
import re

# --- รายชื่อร้านอาหาร ---
RESTAURANT_MENUS = {
    "mama": "image/menu.jpg",
    "pizza": "image/menu.jpg",
    "kfc": "image/menu.jpg",
    "starbucks": "image/menu.jpg",
    "mcd": "image/menu.jpg",
}

# --- ฟังก์ชันแยกเมนู ---
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

        # 1. ถ้าเป็นข้อความจากบอทตัวเอง ให้เมิน
        if message.author == self.bot:
            return

        # 2. ตรวจสอบข้อความต้อนรับจาก Ticket Tool
        if message.author.bot and message.author.name == "Ticket Tool" and message.embeds:
            # สร้าง list ร้านอาหาร
            restaurant_list_str = ""
            for i, name in enumerate(RESTAURANT_MENUS.keys(), 1):
                restaurant_list_str += f"{i}. {name.capitalize()}\n" 

            response_message = (
                "These are the restaurants in the canteen:\n"
                f"{restaurant_list_str}"
                "Type `!menu <name>` to see the menu. eg `!menu mama`"
            )

            await message.channel.send(response_message)
            return

        # 3. ถ้าเป็นข้อความจากบอทตัวอื่น (ที่ไม่ใช่ Ticket Tool ที่เพิ่งเช็กไป) ให้เมิน
        if message.author.bot:
            return

        # 4. โค้ดเดิมสำหรับมนุษย์ (ยังทำงานเหมือนเดิม)
        if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-"):
            content = message.content.strip()
            lower = content.lower()

            # 4.1 เช็ก "restaurant"
            if "restaurant" in lower: 
                restaurant_list_str = ""
                for i, name in enumerate(RESTAURANT_MENUS.keys(), 1):
                    restaurant_list_str += f"{i}. {name.capitalize()}\n" 

                response_message = (
                    "These are the restaurants in the canteen:\n"
                    f"{restaurant_list_str}"
                    "Type `!menu <name>` to see the menu. eg `!menu mama`"
                )

                await message.channel.send(response_message)
                return
            
            # 4.2 เช็กออเดอร์ (ถ้าไม่ได้ขึ้นต้นด้วย !)
            if not content.startswith("!"): 
                menu, note = parse_menu_item(content)

                embed = discord.Embed(
                    title="[S]บันทึกออเดอร์ (WIP) :tropical_drink:",
                    description="ร้านอาหารได้รับออเดอร์ของคุณ และกำลังเตรียมอาหารให้คุณ",
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

            pass

    # --- คำสั่ง !menu (นี่คือส่วนที่แก้ไข) ---
    @commands.command(name="menu")
    async def menu_cmd(self, ctx: commands.Context, restaurant: str = None):
        if restaurant is None:
            await ctx.send("Please specify a restaurant. Example: `!menu mama`")
            return
            
        rest = restaurant.lower()
        path = RESTAURANT_MENUS.get(rest)
        
        if path and os.path.isfile(path):
            # 1. ส่งรูปเมนู (เหมือนเดิม)
            await ctx.send(file=discord.File(path))
            
            # 2. ส่งวิธีสั่งซื้อ (ส่วนที่เพิ่มเข้ามา)
            example_message = (
                "**วิธีสั่งอาหาร:** พิมพ์ชื่อเมนูที่ต้องการได้เลย\n"
                "ตัวอย่าง: `ข้าวผัดกะเพรา`\n"
                "ตัวอย่าง (มีหมายเหตุ): `ข้าวผัดกะเพรา (ไข่ดาวไม่สุก)`"
            )
            await ctx.send(example_message)
            
        else:
            await ctx.send("Sorry, I don't have the menu for that restaurant.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ticket(bot))
