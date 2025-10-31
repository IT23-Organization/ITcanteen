import discord
from discord.ext import commands
import aiohttp
import asyncio

# --- ⚙️ ตั้งค่า (แก้ตรงนี้) ---
BOT_TOKEN = "YOUR_BOT_TOKEN"  # << 1. ใส่ Token ของบอทคุณ
BASE_API_URL = "https://api.yourdomain.com" # << 2. ใส่ URL หลักของ API (เช่น https://api.example.com)
STORE_ID = 1  # << 3. ใส่ ID ของร้านค้าที่ต้องการให้บอทนี้ดูแล

# --- 🏪 ตัวแปรเก็บข้อมูลร้าน (จะถูกเติมอัตโนมัติ) ---
restaurant_data = {
    "name": "ร้าน (กำลังโหลด...)",
    "menu": {}  # เปลี่ยนจาก List เป็น Dictionary เพื่อเก็บข้อมูลสินค้า (ID, ราคา)
}

# --- 🤖 ตั้งค่า Bot และ Intents ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 📡 ฟังก์ชันสำหรับดึงข้อมูลจาก API ---
async def fetch_restaurant_data():
    """
    ดึงข้อมูลร้านและเมนูจาก API ตาม STORE_ID ที่กำหนด
    """
    global restaurant_data
    
    # สร้าง URL สำหรับยิง API
    api_endpoint = f"{BASE_API_URL}/store?store_id={STORE_ID}"
    print(f"กำลังดึงข้อมูลจาก: {api_endpoint}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_endpoint) as response:
                if response.status == 200:
                    data = await response.json() # แปลง .json เป็น dict
                    
                    # 1. ดึงชื่อร้าน
                    # จาก JSON: { "name": "โคเจ", ... } 
                    restaurant_data["name"] = data.get("name", "ร้านไม่มีชื่อ")
                    
                    # 2. สร้างเมนู (Dictionary)
                    # จาก JSON: { "products": [ { "name": "...", "product_id": ..., "price": ... }, ... ] } 
                    
                    # เคลียร์เมนูเก่าก่อน
                    restaurant_data["menu"] = {} 
                    
                    raw_products = data.get("products", [])
                    for item in raw_products:
                        food_name = item.get("name")
                        if food_name:
                            # เก็บข้อมูลสินค้า โดยใช้ชื่อพิมพ์เล็กเป็น key
                            food_name_lower = food_name.lower()
                            restaurant_data["menu"][food_name_lower] = {
                                "id": item.get("product_id"),
                                "price": item.get("price"),
                                "original_name": food_name # เก็บชื่อจริงไว้แสดงผล
                            }
                    
                    print(f"✅ โหลดข้อมูลร้านสำเร็จ: {restaurant_data['name']}")
                    print(f"🛒 เมนูที่พบ: {len(restaurant_data['menu'])} รายการ")
                
                else:
                    print(f"❌ Error: ไม่สามารถดึงข้อมูล API ได้ (Status: {response.status})")
                    restaurant_data["menu"] = {} # เฟลแล้วให้เมนูว่าง
        
        except Exception as e:
            print(f"❌ Error: เกิดข้อผิดพลาดขณะเชื่อมต่อ API: {e}")
            restaurant_data["menu"] = {}

# --- 🚀 Event เมื่อบอทพร้อมทำงาน ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # ดึงข้อมูลร้านทันทีที่บอทเริ่ม
    await fetch_restaurant_data()

# --- 🛒 คำสั่ง !order ---
@bot.command()
async def order(ctx, *, food_name: str):
    """
    รับออเดอร์อาหาร โดยต้องพิมพ์ !order ตามด้วยชื่ออาหาร
    """
    
    if not restaurant_data["menu"]:
        await ctx.send(f"ขออภัยครับ ร้าน **{restaurant_data['name']}** กำลังปิดปรับปรุง (โหลดเมนูไม่สำเร็จ)")
        return

    # แปลงชื่ออาหารที่ผู้ใช้พิมพ์มา
    requested_food = food_name.lower().strip()

    # ตรวจสอบว่าอาหารที่สั่ง (key พิมพ์เล็ก) อยู่ในเมนู (dict) หรือไม่
    if requested_food in restaurant_data["menu"]:
        
        # ดึงรายละเอียดสินค้าจาก dict
        food_details = restaurant_data["menu"][requested_food]
        original_name = food_details["original_name"]
        price = food_details["price"]
        product_id = food_details["id"] # << เราได้ ID สินค้ามาด้วย!

        await ctx.send(f"✅ รับออเดอร์ **{original_name}** ราคา {price} บาท เรียบร้อยครับ!")
        
        # --- (ส่วนเสริม) ---
        # ตรงนี้ คุณสามารถยิง API POST /orders/add ได้เลย
        # เพราะคุณมี
        # - ctx.author.id (เก็บเป็น student_id)
        # - STORE_ID (จากตัวแปรด้านบน)
        # - product_id (จาก food_details)
        # ---------------------

    else:
        # ถ้าไม่เจอ
        await ctx.send(f"❌ ขออภัยครับ **{food_name.strip()}** ไม่มีในเมนูของร้าน **{restaurant_data['name']}** ครับ")

# --- 📋 คำสั่ง !menu (อัปเดต) ---
@bot.command()
async def menu(ctx):
    """
    แสดงเมนูอาหารทั้งหมดที่ดึงมาจาก API
    """
    if restaurant_data["menu"]:
        menu_display_list = []
        # วนลูปจาก .values() ของ dictionary เพื่อดึงรายละเอียด
        for food_details in restaurant_data["menu"].values():
            name = food_details["original_name"]
            price = food_details["price"]
            menu_display_list.append(f"- **{name}** (ราคา {price} บาท)")
        
        menu_text = "\n".join(menu_display_list)
        await ctx.send(f"**เมนูร้าน {restaurant_data['name']}**\n{menu_text}")
    else:
        await ctx.send("ขออภัยครับ ยังไม่มีข้อมูลเมนูในตอนนี้")

# --- 🔁 (คำสั่งเสริม) บังคับโหลดเมนูใหม่ ---
@bot.command()
@commands.is_owner() # ให้เฉพาะเจ้าของบอทใช้ได้
async def reload(ctx):
    """
    บังคับให้บอทดึงข้อมูล API ใหม่
    """
    await ctx.send("🔄 กำลังโหลดข้อมูลร้านและเมนูใหม่...")
    await fetch_restaurant_data()
    await ctx.send(f"✅ โหลดข้อมูลร้าน **{restaurant_data['name']}** ใหม่เรียบร้อย!")


# --- รันบอท ---
try:
    bot.run(BOT_TOKEN)
except discord.errors.LoginFailure:
    print("❌ Error: BOT_TOKEN ไม่ถูกต้อง")
except Exception as e:
    print(f"❌ Error: เกิดปัญหาในการรันบอท: {e}")
