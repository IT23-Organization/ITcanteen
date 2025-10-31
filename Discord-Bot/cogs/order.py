import discord
from discord.ext import commands
import aiohttp
import asyncio

# --- ⚙️ ตั้งค่า (แก้ตรงนี้) ---
BASE_API_URL = "http://localhost:8080" 
STORE_ID = 1  # 2. ใส่ ID ของร้านค้า
TICKET_CHANNEL_PREFIX = "ticket-" # ⭐️ 3. ใส่ "คำนำหน้า" ของช่อง Ticket ที่บอทจะโพสต์เมนู

# ---------------------------------------------------------------------
# 1. สร้างคลาส Cog
# ---------------------------------------------------------------------
class OrderCog(commands.Cog):
    
    # -----------------------------------------------------------------
    # 2. ฟังก์ชัน __init__
    # -----------------------------------------------------------------
    def __init__(self, bot):
        self.bot = bot
        self.restaurant_data = {
            "name": f"ร้าน ID {STORE_ID} (กำลังโหลด...)",
            "menu": {}  # { "ชื่อพิมพ์เล็ก": { id, price, original_name, note } }
        }
        self.fetch_task = self.bot.loop.create_task(self.fetch_restaurant_data())

    # -----------------------------------------------------------------
    # 3. (อัปเดต) ฟังก์ชันดึง API
    # -----------------------------------------------------------------
    async def fetch_restaurant_data(self):
        """
        ดึงข้อมูลร้านและเมนูจาก API
        """
        await self.bot.wait_until_ready() 
        
        store_info_endpoint = f"{BASE_API_URL}/store?store_id={STORE_ID}"
        
        # ⭐️ (ปรับ) แก้ไขกลับเป็น "products" ให้ถูกต้อง
        menu_endpoint = f"{BASE_API_URL}/store/product?store_id={STORE_ID}" 

        async with aiohttp.ClientSession() as session:
            try:
                # --- 1. ดึงชื่อร้าน ---
                print(f"[OrderCog] กำลังดึงชื่อร้านจาก: {store_info_endpoint}")
                async with session.get(store_info_endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.restaurant_data["name"] = data.get("name", f"ร้าน ID {STORE_ID}")
                        print(f"✅ [OrderCog] ได้ชื่อร้าน: {self.restaurant_data['name']}")
                    else:
                        print(f"❌ [OrderCog] ไม่สามารถดึงชื่อร้านได้ (Status: {response.status})")

                # --- 2. ดึงเมนู ---
                print(f"[OrderCog] กำลังดึงเมนูจาก: {menu_endpoint}")
                async with session.get(menu_endpoint) as response:
                    if response.status == 200:
                        raw_products = await response.json() 
                        new_menu = {}
                        
                        for item in raw_products:
                            food_name = item.get("name")
                            if food_name:
                                food_name_lower = food_name.lower()
                                new_menu[food_name_lower] = {
                                    "id": item.get("product_id"),
                                    "price": item.get("price"),
                                    "original_name": food_name,
                                    "note": item.get("note", "") 
                                }
                        
                        self.restaurant_data["menu"] = new_menu
                        print(f"✅ [OrderCog] โหลดเมนูสำเร็จ: {len(self.restaurant_data['menu'])} รายการ")
                    else:
                        print(f"❌ [OrderCog] Error: ไม่สามารถดึงข้อมูลเมนูได้ (Status: {response.status})")
                        self.restaurant_data["menu"] = {}
            
            except Exception as e:
                print(f"❌ [OrderCog] Error: เชื่อมต่อ API ล้มเหลว (เช็คว่า API รันอยู่?) : {e}")
                self.restaurant_data["menu"] = {}

    # -----------------------------------------------------------------
    # 4. คำสั่ง !order ( ⭐️⭐️⭐️ แก้ไขตรงนี้ ⭐️⭐️⭐️ )
    # -----------------------------------------------------------------
    @commands.command()
    async def order(self, ctx, *, item_name_str: str): # ⭐️ (ปรับ) เปลี่ยนชื่อตัวแปร
        """
        ⭐️ (ปรับ) รับออเดอร์อาหาร (รับทีละ 1 รายการ)
        ตัวอย่าง: !order กะเพรา
        """
        
        if not self.restaurant_data["menu"]:
            await ctx.send(f"ขออภัยครับ ร้าน **{self.restaurant_data['name']}** กำลังปิดปรับปรุง (โหลดเมนูไม่สำเร็จ)")
            return

        # ⭐️ (ปรับ) ไม่ต้อง split(',') และไม่ต้องใช้ loop
        
        product_id_to_send = None   
        item_name_to_display = ""  
        
        cleaned_name = item_name_str.lower().strip() 
        
        if cleaned_name in self.restaurant_data["menu"]:
            food_details = self.restaurant_data["menu"][cleaned_name]
            product_id_to_send = food_details["id"]
            
            # ⭐️ (ปรับ) สร้างชื่อที่จะแสดงผล (รวม note)
            name = food_details["original_name"]
            note = food_details.get("note", "")
            note_display = f" ({note})" if note else ""
            item_name_to_display = f"{name}{note_display}"
        
        # ⭐️ (ปรับ) ตรวจสอบว่าหาเมนูเจอหรือไม่
        if not product_id_to_send:
            await ctx.send(f"❌ ขออภัยครับ ไม่พบรายการ: **{item_name_str.strip()}**")
            return
            
        order_endpoint = f"{BASE_API_URL}/orders/add"
        student_id = ctx.author.id 
        
        # ⭐️ (ปรับ) สร้าง payload ให้ส่ง "product_id" (ไม่ใช่ "products_id")
        payload = {
            "student_id": student_id,
            "store_id": STORE_ID,
            "product_id": product_id_to_send # ⭐️ ส่ง ID เดียว
        }

        print(f"payload: {payload}")  # Debug: แสดง payload ที่จะส่ง

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(order_endpoint, json=payload) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        order_id = response_data.get("id", "N/A") 
                        
                        # 1. ดึง "เลขคิว" (queue_number) จาก API response
                        queue_number = response_data.get("queue_number", "N/A")
                        
                        # 2. เพิ่มการแสดงผล queue_number ในข้อความ
                        await ctx.send(
                            f"✅ **รับออเดอร์เรียบร้อยครับ!**\n"
                            # ⭐️ (ปรับ) แสดงชื่อเมนูที่หาเจอแค่ชื่อเดียว
                            f"**รายการ:** {item_name_to_display}\n"
                            f"**เลขที่ออเดอร์:** `{order_id}`\n"
                            f"**🔔 คุณได้คิวที่: {queue_number}**" 
                        )
                    else:
                        error_text = await response.text()
                        await ctx.send(f"❌ เกิดข้อผิดพลาดในการส่งออเดอร์ (Status: {response.status})\n`{error_text}`")
                        
        except Exception as e:
            await ctx.send(f"❌ เกิดข้อผิดพลาดรุนแรงในการเชื่อมต่อ API: {e}")

    # -----------------------------------------------------------------
    # ⭐️ 5. ฟังก์ชัน Helper สำหรับสร้าง Embed เมนู ( ⭐️⭐️⭐️ แก้ไขตรงนี้ ⭐️⭐️⭐️ )
    # -----------------------------------------------------------------
    async def _create_menu_embed(self):
        """
        (Helper) สร้าง Embed เมนูอาหาร (แยก Logic มาจาก !menu)
        จะคืนค่าเป็น Embed object หรือ None (ถ้าไม่มีเมนู)
        """
        if not self.restaurant_data["menu"]:
            return None # คืนค่า None ถ้าไม่มีเมนู

        menu_display_list = []
        example_items = [] 
        
        # วนลูปเพื่อสร้างลิสต์เมนู และดึงชื่อตัวอย่าง
        for i, food_details in enumerate(self.restaurant_data["menu"].values()):
            name = food_details["original_name"]
            price = food_details["price"]
            note = food_details.get("note", "") 
            note_display = f" ({note})" if note else "" 
            menu_display_list.append(f"- **{name}**{note_display} (ราคา {price} บาท)")
            
            # เก็บชื่อตัวอย่าง (แค่ชื่อแรกก็พอ)
            if i < 1: # ⭐️ (ปรับ) เอาแค่ 1 ชื่อ
                example_items.append(name)

        menu_text = "\n".join(menu_display_list)
        
        # สร้าง Embed (เหมือนเดิม)
        embed = discord.Embed(
            title=f"📋 เมนูร้าน {self.restaurant_data['name']}",
            description=menu_text,
            color=discord.Color.green() # เปลี่ยนสีได้ตามชอบ
        )
        
        # ⭐️ (ปรับ) แก้ไขตัวอย่างการสั่งให้เป็นแบบเมนูเดียว
        if example_items:
            example_order_str = example_items[0] # ⭐️ เอาแค่ชื่อแรก
            embed.add_field(
                name="💡 ตัวอย่างการสั่งอาหาร",
                value=f"พิมพ์ `!order {example_order_str}`", # ⭐️ ลบส่วน (,) ออก
                inline=False
            )
        else:
            embed.add_field(
                name="💡 ตัวอย่างการสั่งอาหาร",
                value="พิมพ์ `!order <ชื่ออาหาร>`",
                inline=False
            )
        
        return embed # คืนค่า Embed ที่สร้างเสร็จ

    # -----------------------------------------------------------------
    # ⭐️ (ปรับ) 6. คำสั่ง !menu (เหมือนเดิม)
    # -----------------------------------------------------------------
    @commands.command()
    async def menu(self, ctx):
        """
        แสดงเมนูอาหารทั้งหมดที่ดึงมาจาก API
        """
        embed = await self._create_menu_embed() # ⭐️ เรียกใช้ Helper
        
        if embed:
            await ctx.send(embed=embed) # ส่งเป็น embed
        else:
            await ctx.send("ขออภัยครับ ยังไม่มีข้อมูลเมนูในตอนนี้")

    # --- 🔁 คำสั่ง !reload (เหมือนเดิม) ---
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        """
        บังคับให้บอทดึงข้อมูล API ใหม่
        """
        await ctx.send("🔄 กำลังโหลดข้อมูลร้านและเมนูใหม่...")
        await self.fetch_restaurant_data()
        await ctx.send(f"✅ โหลดข้อมูลร้าน **{self.restaurant_data['name']}** ใหม่เรียบร้อย!")

    # -----------------------------------------------------------------
    # ⭐️ (เพิ่ม) 7. Event Listener ดักฟังตอนสร้างช่อง (เหมือนเดิม)
    # -----------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        ทำงานอัตโนมัติเมื่อมีช่องใหม่ถูกสร้างขึ้นใน Server
        """
        # 1. เช็คว่าช่องที่สร้างเป็น Text Channel หรือไม่
        if not isinstance(channel, discord.TextChannel):
            return
            
        # 2. เช็คว่าชื่อช่องตรงกับที่เราตั้งค่าไว้หรือไม่ (เช่น "ticket-001")
        if channel.name.startswith(TICKET_CHANNEL_PREFIX):
            
            print(f"[OrderCog] ตรวจพบช่อง Ticket ใหม่: {channel.name}. กำลังส่งเมนู...")
            
            # 3. หน่วงเวลาเล็กน้อย (เผื่อบอท Ticket ยังตั้งค่า permission ไม่เสร็จ)
            await asyncio.sleep(1) 
            
            # 4. เรียกใช้ Helper เพื่อสร้าง Embed
            embed = await self._create_menu_embed()
            
            # 5. ส่ง Embed
            if embed:
                try:
                    await channel.send(
                        f"ยินดีต้อนรับครับ! นี่คือเมนูของร้าน **{self.restaurant_data['name']}**\n"
                        # ⭐️ (ปรับ) แก้ข้อความต้อนรับใน Ticket ให้ตรง
                        "คุณสามารถพิมพ์ `!order <ชื่ออาหาร>` เพื่อสั่งได้เลยครับ"
                    )
                    await channel.send(embed=embed)
                except discord.errors.Forbidden:
                    print(f"❌ [OrderCog] ไม่มีสิทธิ์ส่งข้อความในช่อง {channel.name}")
            else:
                # กรณีเมนูโหลดไม่สำเร็จ
                try:
                    await channel.send(f"ขออภัยครับ ร้าน **{self.restaurant_data['name']}** กำลังปิดปรับปรุง (โหลดเมนูไม่สำเร็จ)")
                except discord.errors.Forbidden:
                    print(f"❌ [OrderCog] ไม่มีสิทธิ์ส่งข้อความในช่อง {channel.name}")


# ---------------------------------------------------------------------
# 5. ฟังก์ชัน setup (ประตูทางเข้า)
# ---------------------------------------------------------------------
async def setup(bot):
    await bot.add_cog(OrderCog(bot))
    # ⭐️ (ปรับ) อัปเดตชื่อเวอร์ชัน
    print("[OrderCog] Cog 'order' (v6 - Single Order Only) has been loaded.")
