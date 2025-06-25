import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔄 ตัวแปรโค้ดเริ่มต้น
current_code = "DEFAULT123"

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"🤖 Logged in as {bot.user}")

# ⚙️ ตั้งค่า code กลาง
@bot.tree.command(name="setcode", description="ตั้งรหัสคูปองเริ่มต้น")
@app_commands.describe(code="รหัสคูปองใหม่")
async def setcode(interaction: discord.Interaction, code: str):
    global current_code
    current_code = code
    await interaction.response.send_message(f"✅ ตั้ง code ใหม่เป็น `{code}`")

# 📨 ใช้ code ล่าสุด
@bot.tree.command(name="coupon", description="ใช้โค้ดปัจจุบันพร้อมอีเมลของคุณ")
@app_commands.describe(email="อีเมลของคุณ")
async def coupon(interaction: discord.Interaction, email: str):
    url = f"https://coupon.devplay.com/coupon/cookieruntoa/en?code={current_code}&email={email}"
    await interaction.response.send_message(f"🔗 ลิงก์ของคุณ: {url}")

# ✍️ กรอกโค้ดเอง
@bot.tree.command(name="coupon_manual", description="กรอกโค้ดและอีเมลด้วยตนเอง")
@app_commands.describe(code="รหัสคูปอง", email="อีเมลของคุณ")
async def coupon_manual(interaction: discord.Interaction, code: str, email: str):
    url = f"https://coupon.devplay.com/coupon/cookieruntoa/en?code={code}&email={email}"
    await interaction.response.send_message(f"🔗 ลิงก์ของคุณ: {url}")

bot.run(TOKEN)
