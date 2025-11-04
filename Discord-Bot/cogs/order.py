import discord
from discord.ext import commands
from discord import app_commands # 1. (เพิ่ม) Import app_commands
import aiohttp
import asyncio
import re

# --- ⚙️ ตั้งค่า ---
BASE_API_URL = "http://localhost:8080" # 1. API ของคุณ
TICKET_CHANNEL_PREFIX = "ticket-"      # 2. คำนำหน้าช่องทิกเก็ต
TICKET_TOOL_BOT_NAME = "Ticket Tool"   # 3. ชื่อบอทที่สร้างทิกเก็ต
# ---------------------------------

class OrderCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.api_base_url = BASE_API_URL
        self.ticket_prefix = TICKET_CHANNEL_PREFIX
        
        # --- ตัวแปรสำหรับเก็บข้อมูล ---
        
        # 1. (แก้ไข) เก็บรายชื่อและ URL เมนูของร้านค้า
        #    { 1: { "name": "โคเจ", "menu_url": "http://..." } }
        self.stores_cache = {}
        
        # 2. เก็บเมนู (products) ของร้านที่เคยโหลดแล้ว
        self.menu_cache = {}
        
        # 3. เก็บว่าช่องทิกเก็ตนี้ "เลือกร้านอะไรอยู่"
        self.channel_states = {}

        self.store_fetch_task = self.bot.loop.create_task(self.fetch_all_stores())

    # -----------------------------------------------------------------
    # (แก้ไข) 1. ฟังก์ชันดึง "รายชื่อร้านค้าทั้งหมด"
    # -----------------------------------------------------------------
    async def fetch_all_stores(self):
        """
        (API: GET /store) ดึงรายชื่อร้านค้าทั้งหมดมาเก็บไว้ใน cache
        """
        await self.bot.wait_until_ready()
        endpoint = f"{self.api_base_url}/store" #
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        stores_list = await response.json()
                        self.stores_cache.clear()
                        for store in stores_list:
                            # (แก้ไข) เก็บ cả ชื่อ และ menu_url
                            self.stores_cache[store.get("store_id")] = {
                                "name": store.get("name"),
                                "menu_url": store.get("menu_url") #
                            }
                        print(f"[OrderCog] ✅ โหลดรายชื่อร้านค้าสำเร็จ: {len(self.stores_cache)} ร้าน")
                    else:
                        print(f"❌ [OrderCog] ไม่สามารถดึงรายชื่อร้านค้าได้ (Status: {response.status})")
        except Exception as e:
            print(f"❌ [OrderCog] เกิด Error ตอนดึงรายชื่อร้านค้า: {e}")

    # -----------------------------------------------------------------
    # 2. ฟังก์ชันดึง "เมนูของร้านที่เลือก"
    # -----------------------------------------------------------------
    async def fetch_store_menu(self, store_id: int):
        """
        (API: GET /store/product) ดึงเมนูของร้านที่ระบุ
        """
        if store_id in self.menu_cache:
            return self.menu_cache[store_id]
            
        endpoint = f"{self.api_base_url}/store/product?store_id={store_id}" #
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        products_list = await response.json()
                        new_menu = {}
                        for item in products_list:
                            food_name = item.get("name")
                            if food_name:
                                new_menu[food_name.lower().strip()] = {
                                    "id": item.get("product_id"),
                                    "price": item.get("price"),
                                    "original_name": food_name
                                }
                        self.menu_cache[store_id] = new_menu
                        print(f"[OrderCog] ✅ โหลดเมนู (products) ร้าน ID {store_id} สำเร็จ")
                        return new_menu
                    else:
                        print(f"❌ [OrderCog] ไม่สามารถดึงเมนู (products) ร้าน ID {store_id} (Status: {response.status})")
                        return None
        except Exception as e:
            print(f"❌ [OrderCog] เกิด Error ตอนดึงเมนู (products): {e}")
            return None

    # -----------------------------------------------------------------
    # 3. ฟังก์ชันแยก "ชื่อเมนู" และ "หมายเหตุ"
    # -----------------------------------------------------------------
    def parse_order_string(self, text: str):
        pattern = r"(.*?)\s*\((.*?)\)$"
        match = re.search(pattern, text)
        
        if match:
            menu_name = match.group(1).strip()
            note = match.group(2).strip()
            return menu_name, note
        else:
            menu_name = text.strip()
            return menu_name, None

    # -----------------------------------------------------------------
    # (แก้ไข) 4. Listener: ทำงานเมื่อเปิดทิกเก็ต (Requirement 1)
    # -----------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot:
            return

        if message.author.bot and message.author.name == TICKET_TOOL_BOT_NAME and message.embeds:
            
            if not self.stores_cache:
                await message.channel.send("🔄 กำลังโหลดรายชื่อร้านค้าสักครู่...")
                await self.fetch_all_stores()

            if not self.stores_cache:
                await message.channel.send("❌ ขออภัย, ไม่สามารถติดต่อ API เพื่อดึงรายชื่อร้านค้าได้")
                return

            # (แก้ไข) สร้าง List รายชื่อร้านจาก cache ใหม่
            store_list_str = ""
            for store_id, store_data in self.stores_cache.items():
                store_list_str += f"• **{store_data['name']}**\n"
            
            response_message = (
                "ยินดีต้อนรับครับ! กรุณาเลือกร้านอาหารที่ต้องการ:\n"
                f"{store_list_str}\n"
                # 2. (เปลี่ยน) อัปเดตข้อความเป็น Slash Command
                "**วิธีเลือก:** พิมพ์ `/menu <ชื่อร้านอาหาร>` (เช่น `/menu โคเจ`)"
            )
            
            await message.channel.send(response_message)
            return

        if message.author.bot:
            return
            
        pass

    # -----------------------------------------------------------------
    # (แก้ไข) 5. คำสั่ง /menu (Requirement 2)
    # -----------------------------------------------------------------
    # 3. (เปลี่ยน) ใช้ @app_commands.command
    @app_commands.command(name="menu")
    @app_commands.describe(store_name="ชื่อร้านอาหารที่ต้องการดูเมนู (เช่น โคเจ)")
    # 4. (เปลี่ยน) ใช้ interaction และ store_name เป็น non-optional
    async def menu_cmd(self, interaction: discord.Interaction, store_name: str):
        
        # 5. (เปลี่ยน) ใช้ interaction.channel
        if not interaction.channel.name.startswith(self.ticket_prefix):
            # 6. (เปลี่ยน) ใช้ interaction.response.send_message
            await interaction.response.send_message("คำสั่งนี้สามารถใช้ได้ในช่องทิกเก็ตเท่านั้น", ephemeral=True)
            return

        # 7. (เพิ่ม) Defer การตอบกลับ เพราะต้องใช้เวลาโหลด API
        await interaction.response.defer()
            
        # (แก้ไข) ค้นหาร้านจาก cache ใหม่
        found_store = None
        search_name = store_name.lower().strip()
        
        for store_id, store_data in self.stores_cache.items():
            if search_name == store_data['name'].lower():
                found_store = {
                    "id": store_id, 
                    "name": store_data['name'],
                    "menu_url": store_data.get('menu_url') # ดึง URL รูปเมนู
                }
                break
        
        if not found_store:
            # 8. (เปลี่ยน) ใช้ interaction.followup.send
            await interaction.followup.send(f"❌ ไม่พบร้านอาหารชื่อ: `{store_name}`")
            return
            
        store_id = found_store["id"]
        store_name = found_store["name"]
        menu_url = found_store.get("menu_url") # นี่คือลิงก์รูปภาพ

        # 9. (เปลี่ยน) ใช้ interaction.channel.id
        self.channel_states[interaction.channel.id] = {"store_id": store_id, "store_name": store_name}
        
        # (สำคัญ) โหลด "รายการสินค้า" (products) ไว้ใน cache เสมอ
        menu_data = await self.fetch_store_menu(store_id)

        # --- (บล็อกแก้ไขหลัก) ---

        if menu_url:
            print(f"[OrderCog] ร้าน {store_name} มี menu_url: {menu_url}")
            embed = discord.Embed(
                title=f"📋 เมนูร้าน {store_name}",
                color=discord.Color.blue()
            )
            embed.set_image(url=menu_url)
        
        else:
            print(f"[OrderCog] ร้าน {store_name} ไม่มี menu_url, ใช้เมนูแบบข้อความแทน")
            if not menu_data:
                # 10. (เปลี่ยน) ใช้ interaction.followup.send
                await interaction.followup.send(f"❌ ขออภัย, ไม่สามารถดึงเมนูร้าน **{store_name}** ได้ในขณะนี้")
                return
            
            menu_display_list = []
            for item in menu_data.values():
                menu_display_list.append(f"- **{item['original_name']}** (ราคา {item['price']} บาท)")
            menu_text = "\n".join(menu_display_list)
            
            embed = discord.Embed(
                title=f"📋 เมนูร้าน {store_name}",
                description=menu_text,
                color=discord.Color.blue()
            )
        
        if menu_data and list(menu_data.values()): 
            example_name = list(menu_data.values())[0]['original_name'] 
            embed.add_field(
                name="💡 วิธีสั่งอาหาร",
                # 11. (เปลี่ยน) อัปเดตข้อความเป็น Slash Command
                value=f"พิมพ์ `/order {example_name}`\n"
                      f"หรือ `/order {example_name} (สามารถระบุข้อความเพิ่มเติมถึงร้านค้า)`",
                inline=False
            )
        else:
             embed.set_footer(text="ร้านนี้ยังไม่มีรายการอาหารในระบบ")
        
        # 12. (เปลี่ยน) ใช้ interaction.followup.send
        await interaction.followup.send(embed=embed)
        # --- (จบ บล็อกแก้ไขหลัก) ---

    # -----------------------------------------------------------------
    # 6. คำสั่ง /order (Requirement 3)
    # -----------------------------------------------------------------
    # 13. (เปลี่ยน) ใช้ @app_commands.command
    @app_commands.command(name="order")
    @app_commands.describe(order_string="รายการอาหารที่สั่ง เช่น 'กะเพรา (ไม่เผ็ด)'")
    # 14. (เปลี่ยน) ใช้ interaction และ order_string เป็น non-optional
    async def order_cmd(self, interaction: discord.Interaction, order_string: str):
        
        # 15. (เปลี่ยน) ใช้ interaction.channel
        if not interaction.channel.name.startswith(self.ticket_prefix):
            # 16. (เปลี่ยน) ใช้ interaction.response.send_message
            await interaction.response.send_message("คำสั่งนี้สามารถใช้ได้ในช่องทิกเก็ตเท่านั้น", ephemeral=True)
            return

        # 17. (เพิ่ม) Defer การตอบกลับ
        await interaction.response.defer()
            
        # 18. (เปลี่ยน) ใช้ interaction.channel.id
        channel_state = self.channel_states.get(interaction.channel.id)
        if not channel_state:
            # 19. (เปลี่ยน) ใช้ interaction.followup.send และอัปเดตข้อความ
            await interaction.followup.send("กรุณาเลือกร้านก่อนครับ พิมพ์ `/menu <ชื่อร้าน>`")
            return
            
        store_id = channel_state["store_id"]
        store_name = channel_state["store_name"]

        food_name, note = self.parse_order_string(order_string)
        
        menu_data = self.menu_cache.get(store_id)
        if not menu_data:
            # 20. (เปลี่ยน) ใช้ interaction.followup.send และอัปเดตข้อความ
            await interaction.followup.send("เกิดข้อผิดพลาด, กรุณาพิมพ์ `/menu` ใหม่อีกครั้งครับ")
            return

        food_details = menu_data.get(food_name.lower())
        
        if not food_details:
            # 21. (เปลี่ยน) ใช้ interaction.followup.send
            await interaction.followup.send(f"❌ ไม่พบเมนู: **{food_name}** ในร้าน {store_name}")
            return
            
        product_id = food_details["id"]
        original_name = food_details["original_name"]

        order_endpoint = f"{self.api_base_url}/orders/add" #
        payload = {
            "student_id": interaction.user.id, # 22. (เปลี่ยน) ใช้ interaction.user.id
            "store_id": store_id,
            "product_id": product_id
        }
        
        # 23. (เปลี่ยน) ใช้ interaction.followup.send สำหรับข้อความ "กำลังส่ง"
        # สังเกต: เราใช้ followup ที่นี่ เพราะเรา defer ไปแล้ว
        await interaction.followup.send("...กำลังส่งออเดอร์... 🚀")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(order_endpoint, json=payload) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        order_id = response_data.get("id", "N/A")
                        queue_number = response_data.get("queue_number", "N/A") #
                        
                        title = "✅ รับออเดอร์เรียบร้อย!"
                        desc = (
                            f"**ร้าน:** {store_name}\n"
                            f"**รายการ:** {original_name}\n"
                        )
                        if note:
                            desc += f"**หมายเหตุ:** {note}\n"
                        
                        desc += f"\n**เลขที่ออเดอร์:** `{order_id}`\n"
                        desc += f"**🔔 คุณได้คิวที่: {queue_number}**"
                        
                        embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
                        # 24. (เปลี่ยน) ใช้ followup.send อีกครั้งเพื่อส่ง Embed
                        # (Slash command สามารถ followup ได้หลายครั้ง)
                        await interaction.followup.send(embed=embed)
                        
                    else:
                        error_text = await response.text()
                        # 25. (เปลี่ยน) ใช้ followup.send สำหรับ error
                        await interaction.followup.send(f"❌ เกิดข้อผิดพลาดในการส่งออเดอร์ (Status: {response.status})\n`{error_text}`")
                        
        except Exception as e:
            # 26. (เปลี่ยน) ใช้ followup.send สำหรับ exception
            await interaction.followup.send(f"❌ เกิดข้อผิดพลาดรุนแรงในการเชื่อมต่อ API: {e}")

    # -----------------------------------------------------------------
    # 7. ฟังก์ชันล้าง state เมื่อปิดทิกเก็ต (ไม่เปลี่ยนแปลง)
    # -----------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.id in self.channel_states:
            try:
                del self.channel_states[channel.id]
                print(f"[OrderCog] ล้าง State ของช่อง {channel.name} (ID: {channel.id}) ที่ถูกปิดแล้ว")
            except KeyError:
                pass

# -----------------------------------------------------------------
# 8. ฟังก์ชัน setup (ประตูทางเข้า) (ไม่เปลี่ยนแปลง)
# -----------------------------------------------------------------
async def setup(bot):
    await bot.add_cog(OrderCog(bot))
    print("[OrderCog] Cog 'OrderCog' (v_MultiStore_API_Image) has been loaded.")