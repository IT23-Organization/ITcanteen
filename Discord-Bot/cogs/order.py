import discord
from discord.ext import commands
import aiohttp
import asyncio
import re

# --- ⚙️ ตั้งค่า (แก้ตรงนี้) ---
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
        
        # 1. เก็บรายชื่อร้านค้าทั้งหมด
        #    { 1: "โคเจ", 2: "ร้านป้า" }
        self.stores_cache = {}
        
        # 2. เก็บเมนูของร้านที่เคยโหลดแล้ว
        #    { 1: { "กะเพรา": { id: 101, ... }, "ไข่เจียว": { id: 102, ... } } }
        self.menu_cache = {}
        
        # 3. (สำคัญ) เก็บว่าช่องทิกเก็ตนี้ "เลือกร้านอะไรอยู่"
        #    { channel_id_1: { "store_id": 1, "store_name": "โคเจ" },
        #      channel_id_2: { "store_id": 2, "store_name": "ร้านป้า" } }
        self.channel_states = {}

        # สั่งให้บอทเริ่มดึงรายชื่อร้านค้าทั้งหมดทันทีที่เปิด
        self.store_fetch_task = self.bot.loop.create_task(self.fetch_all_stores())

    # -----------------------------------------------------------------
    # (ใหม่) 1. ฟังก์ชันดึง "รายชื่อร้านค้าทั้งหมด"
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
                        # เคลียร์ cache เก่าและสร้างใหม่
                        self.stores_cache.clear()
                        for store in stores_list:
                            self.stores_cache[store.get("store_id")] = store.get("name")
                        print(f"[OrderCog] ✅ โหลดรายชื่อร้านค้าสำเร็จ: {len(self.stores_cache)} ร้าน")
                    else:
                        print(f"❌ [OrderCog] ไม่สามารถดึงรายชื่อร้านค้าได้ (Status: {response.status})")
        except Exception as e:
            print(f"❌ [OrderCog] เกิด Error ตอนดึงรายชื่อร้านค้า: {e}")

    # -----------------------------------------------------------------
    # (ใหม่) 2. ฟังก์ชันดึง "เมนูของร้านที่เลือก"
    # -----------------------------------------------------------------
    async def fetch_store_menu(self, store_id: int):
        """
        (API: GET /store/product) ดึงเมนูของร้านที่ระบุ
        """
        # ถ้ามีใน cache แล้ว ให้ใช้ซ้ำ
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
                        # เก็บเข้า cache
                        self.menu_cache[store_id] = new_menu
                        print(f"[OrderCog] ✅ โหลดเมนูร้าน ID {store_id} สำเร็จ: {len(new_menu)} รายการ")
                        return new_menu
                    else:
                        print(f"❌ [OrderCog] ไม่สามารถดึงเมนูร้าน ID {store_id} (Status: {response.status})")
                        return None
        except Exception as e:
            print(f"❌ [OrderCog] เกิด Error ตอนดึงเมนู: {e}")
            return None

    # -----------------------------------------------------------------
    # (ใหม่) 3. ฟังก์ชันแยก "ชื่อเมนู" และ "หมายเหตุ"
    # -----------------------------------------------------------------
    def parse_order_string(self, text: str):
        """
        แยก "กะเพรา (ไข่ดาว)" ออกเป็น ("กะเพรา", "ไข่ดาว")
        """
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
        # 1. ถ้าเป็นข้อความจากบอทตัวเอง ให้เมิน
        if message.author == self.bot:
            return

        # 2. (Requirement 1) ตรวจสอบข้อความต้อนรับจาก Ticket Tool
        if message.author.bot and message.author.name == TICKET_TOOL_BOT_NAME and message.embeds:
            
            # ถ้ายังโหลดรายชื่อร้านไม่เสร็จ (เช่น บอทเพิ่งเปิด)
            if not self.stores_cache:
                await message.channel.send("🔄 กำลังโหลดรายชื่อร้านค้าสักครู่...")
                await self.fetch_all_stores() # บังคับโหลดใหม่

            if not self.stores_cache:
                await message.channel.send("❌ ขออภัย, ไม่สามารถติดต่อ API เพื่อดึงรายชื่อร้านค้าได้")
                return

            # สร้าง List รายชื่อร้าน
            store_list_str = ""
            for store_id, store_name in self.stores_cache.items():
                store_list_str += f"• **{store_name}**\n"
            
            response_message = (
                "ยินดีต้อนรับครับ! กรุณาเลือกร้านอาหารที่ต้องการ:\n"
                f"{store_list_str}\n"
                "**วิธีเลือก:** พิมพ์ `!menu <ชื่อร้านอาหาร>` (เช่น `!menu โคเจ`)"
            )
            
            await message.channel.send(response_message)
            return

        # 3. ถ้าเป็นบอทตัวอื่น (ที่ไม่ใช่ Ticket Tool) ให้เมิน
        if message.author.bot:
            return
            
        # 4. ถ้าข้อความจากคน (ที่ไม่ใช่คำสั่ง) ให้เมินไปเลย
        # (เราจะใช้เฉพาะคำสั่ง !menu และ !order เท่านั้น)
        pass

    # -----------------------------------------------------------------
    # (แก้ไข) 5. คำสั่ง !menu (Requirement 2)
    # -----------------------------------------------------------------
    @commands.command(name="menu")
    async def menu_cmd(self, ctx: commands.Context, *, store_name: str = None):
        
        # ต้องอยู่ในช่องทิกเก็ตเท่านั้น
        if not ctx.channel.name.startswith(self.ticket_prefix):
            return

        if store_name is None:
            await ctx.send("กรุณาระบุชื่อร้านครับ. เช่น `!menu โคเจ`")
            return
            
        # ค้นหาร้านจาก cache
        found_store = None
        search_name = store_name.lower().strip()
        
        for store_id, name in self.stores_cache.items():
            if search_name == name.lower():
                found_store = {"id": store_id, "name": name}
                break
        
        if not found_store:
            await ctx.send(f"❌ ไม่พบร้านอาหารชื่อ: `{store_name}`")
            return
            
        store_id = found_store["id"]
        store_name = found_store["name"]

        # (สำคัญ) "ล็อก" ช่องนี้ไว้กับร้านนี้
        self.channel_states[ctx.channel.id] = {"store_id": store_id, "store_name": store_name}
        
        await ctx.send(f"กำลังดึงเมนูร้าน **{store_name}**...")
        
        # ดึงเมนู (จาก API หรือ cache)
        menu_data = await self.fetch_store_menu(store_id)
        
        if not menu_data:
            await ctx.send(f"❌ ขออภัย, ไม่สามารถดึงเมนูร้าน **{store_name}** ได้ในขณะนี้")
            return
            
        # สร้าง Embed เมนู
        menu_display_list = []
        for item in menu_data.values():
            menu_display_list.append(f"- **{item['original_name']}** (ราคา {item['price']} บาท)")

        menu_text = "\n".join(menu_display_list)
        
        embed = discord.Embed(
            title=f"📋 เมนูร้าน {store_name}",
            description=menu_text,
            color=discord.Color.blue()
        )
        
        # (Requirement 2) เพิ่มตัวอย่างวิธีสั่ง
        example_name = list(menu_data.values())[0]['original_name'] # เอาชื่อเมนูแรกมาเป็นตัวอย่าง
        embed.add_field(
            name="💡 วิธีสั่งอาหาร",
            value=f"พิมพ์ `!order {example_name}`\n"
                  f"หรือ `!order {example_name} (เพิ่มไข่ดาว)`",
            inline=False
        )
        
        await ctx.send(embed=embed)

    # -----------------------------------------------------------------
    # (ใหม่) 6. คำสั่ง !order (Requirement 3)
    # -----------------------------------------------------------------
    @commands.command(name="order")
    async def order_cmd(self, ctx: commands.Context, *, order_string: str = None):
        
        # ต้องอยู่ในช่องทิกเก็ตเท่านั้น
        if not ctx.channel.name.startswith(self.ticket_prefix):
            return

        if order_string is None:
            await ctx.send("กรุณาระบุเมนูที่ต้องการสั่งครับ. เช่น `!order กะเพรา`")
            return
            
        # 1. เช็กว่าเลือกร้านหรือยัง
        channel_state = self.channel_states.get(ctx.channel.id)
        if not channel_state:
            await ctx.send("กรุณาเลือกร้านก่อนครับ พิมพ์ `!menu <ชื่อร้าน>`")
            return
            
        store_id = channel_state["store_id"]
        store_name = channel_state["store_name"]

        # 2. แยกชื่อเมนูและหมายเหตุ (Requirement 3)
        food_name, note = self.parse_order_string(order_string)
        
        # 3. ค้นหา product_id จากเมนูใน cache
        menu_data = self.menu_cache.get(store_id)
        if not menu_data:
            # เกิดกรณีนี้ได้ถ้าบอท restart แต่ state ไม่หาย
            await ctx.send("เกิดข้อผิดพลาด, กรุณาพิมพ์ `!menu` ใหม่อีกครั้งครับ")
            return

        food_details = menu_data.get(food_name.lower())
        
        if not food_details:
            await ctx.send(f"❌ ไม่พบเมนู: **{food_name}** ในร้าน {store_name}")
            return
            
        product_id = food_details["id"]
        original_name = food_details["original_name"]

        # 4. ส่งออเดอร์ไปที่ API (Requirement 3)
        order_endpoint = f"{self.api_base_url}/orders/add" #
        payload = {
            "student_id": ctx.author.id,
            "store_id": store_id,
            "product_id": product_id
            # (หมายเหตุ: API MANUAL_th.md ไม่มีช่องสำหรับ "note"
            #  ดังนั้นเราจะส่งแค่ product_id แต่จะแสดง "note" ให้ลูกค้ายืนยันเอง)
        }
        
        await ctx.send("...กำลังส่งออเดอร์... 🚀")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(order_endpoint, json=payload) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        order_id = response_data.get("id", "N/A")
                        queue_number = response_data.get("queue_number", "N/A") #
                        
                        # (Requirement 3) แสดงผลสรุป
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
                        await ctx.send(embed=embed)
                        
                    else:
                        error_text = await response.text()
                        await ctx.send(f"❌ เกิดข้อผิดพลาดในการส่งออเดอร์ (Status: {response.status})\n`{error_text}`")
                        
        except Exception as e:
            await ctx.send(f"❌ เกิดข้อผิดพลาดรุนแรงในการเชื่อมต่อ API: {e}")

    # -----------------------------------------------------------------
    # (ใหม่) 7. ฟังก์ชันล้าง state เมื่อปิดทิกเก็ต
    # -----------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.id in self.channel_states:
            try:
                del self.channel_states[channel.id]
                print(f"[OrderCog] ล้าง State ของช่อง {channel.name} (ID: {channel.id}) ที่ถูกปิดแล้ว")
            except KeyError:
                pass # ไม่เป็นไรถ้ามันหายไปก่อนแล้ว


# -----------------------------------------------------------------
# 8. ฟังก์ชัน setup (ประตูทางเข้า)
# -----------------------------------------------------------------
async def setup(bot):
    await bot.add_cog(OrderCog(bot))
    print("[OrderCog] Cog 'OrderCog' (v_MultiStore_API) has been loaded.")
