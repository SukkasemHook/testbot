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
GUILD_ID = discord.Object(id=1387050215495700500)
current_code = "DEFAULT123"
raw_users = os.getenv("USERS")
raw_send_user = os.getenv("USERS_ID")

if not raw_users:
    raise ValueError("❌ ไม่พบตัวแปร USERS ใน environment หรือค่าว่าง")

try:
    users = json.loads(raw_users)
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decode error: {e}")

try:
    users_send = json.loads(raw_send_user)
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decode error: {e}")


@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"✅ Synced {len(synced)} commands to guild")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"🤖 Logged in as {bot.user}")

# ⚙️ ตั้งค่า code กลาง
@bot.tree.command(name="setcode", description="ตั้งรหัสคูปองเริ่มต้น", guild=GUILD_ID)
@app_commands.describe(code="รหัสคูปองใหม่")
async def setcode(interaction: discord.Interaction, code: str):
    global current_code
    current_code = code
    await interaction.response.send_message(f"✅ ตั้ง code ใหม่เป็น `{code}`")

# 📨 ใช้ code ล่าสุด
@bot.tree.command(name="coupon", description="ใช้โค้ดปัจจุบันพร้อมอีเมลของคุณ", guild=GUILD_ID)
@app_commands.describe(email="อีเมลของคุณ")
async def coupon(interaction: discord.Interaction, email: str):
    url = f"https://coupon.devplay.com/coupon/cookieruntoa/en?code={current_code}&email={email}"
    await interaction.response.send_message(f"🔗 ลิงก์ของคุณ: {url}")

# ✍️ กรอกโค้ดเอง
@bot.tree.command(name="coupon_manual", description="กรอกโค้ดและอีเมลด้วยตนเอง", guild=GUILD_ID)
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

@bot.tree.command(name="code_by_name", description="เลือกรายชื่อเพื่อรับลิงก์คูปอง", guild=GUILD_ID)
async def coupon_dropdown(interaction: discord.Interaction):
    await interaction.response.send_message("📋 กรุณาเลือกชื่อ:", view=DropdownView(), ephemeral=True)


@bot.tree.command(name="sendcode", description="ส่งโค้ดให้ทุกคนใน list", guild=GUILD_ID)
@app_commands.describe(code="โค้ดที่ต้องการส่ง")
async def send_code(interaction: discord.Interaction, code: str):
    await interaction.response.send_message(f"📨 เริ่มส่งโค้ด `{code}` ไปยังผู้ใช้ในรายการ...", ephemeral=True)

    sent = 0
    failed = 0

    for entry in users_send:
        try:
            user = await bot.fetch_user(entry["dis_id"])
            url = f"https://coupon.devplay.com/coupon/cookieruntoa/th?code={code}&email={entry['mid']}"

            await user.send(
                f"🎁 สวัสดี {entry['name']}!\nโค้ดของคุณคือ: `{code}`\nกดที่นี่เพื่อใช้งาน:\n{url}"
            )
            sent += 1
        except discord.Forbidden:
            failed += 1
        except Exception as e:
            print(f"❌ Error ส่งหา {entry['name']} ({entry['dis_id']}): {e}")
            failed += 1

    await interaction.followup.send(
        f"✅ ส่งสำเร็จ {sent} คน | ❌ ล้มเหลว {failed} คน", ephemeral=True
    )



bot.run(TOKEN)
