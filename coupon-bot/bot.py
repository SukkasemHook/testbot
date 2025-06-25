import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔄 ตัวแปรโค้ดเริ่มต้น
current_code = "DEFAULT123"
raw_users = os.getenv("USERS")

if not raw_users:
    raise ValueError("❌ ไม่พบตัวแปร USERS ใน environment หรือค่าว่าง")

try:
    users = json.loads(raw_users)
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decode error: {e}")

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

class UserDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=user["name"], value=user["email"])
            for user in users
        ]
        super().__init__(
            placeholder="เลือกชื่อผู้ใช้...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        email = self.values[0]
        user = next((u for u in users if u["email"] == email), None)
        if user:
            url = f"https://coupon.devplay.com/coupon/cookieruntoa/th?code={current_code}&email={email}"
            await interaction.response.send_message(f"🔗 **{user['name']}**: {url}", ephemeral=True)

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(UserDropdown())

@bot.tree.command(name="coupon_dropdown", description="เลือกรายชื่อเพื่อรับลิงก์คูปอง")
async def coupon_dropdown(interaction: discord.Interaction):
    await interaction.response.send_message("📋 กรุณาเลือกชื่อ:", view=DropdownView(), ephemeral=True)


bot.run(TOKEN)
