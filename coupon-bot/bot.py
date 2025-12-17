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
raw_send_user = os.getenv("USERS_ID")
raw_users_7k = os.getenv("USERS_7K")

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

try:
    users7k_send = json.loads(raw_users_7k)
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decode error: {e}")



@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} global commands")
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

@bot.tree.command(name="code_by_name", description="เลือกรายชื่อเพื่อรับลิงก์คูปอง")
async def coupon_dropdown(interaction: discord.Interaction):
    await interaction.response.send_message("📋 กรุณาเลือกชื่อ:", view=DropdownView(), ephemeral=True)


class CodeView(discord.ui.View):
    def __init__(self, code_url: str):
        super().__init__()
        self.add_item(discord.ui.Button(
            label="📩 Redeem Now",
            url=code_url
        ))

async def send_code_card_dm(user: discord.User, code: str, player_name: str, mid: str):
    code_url = f"https://coupon.devplay.com/coupon/cookieruntoa/th?code={code}&email={mid}"

    embed = discord.Embed(
        title=f"🥳 {player_name} Guess what? Your surprise gift is here! 🎁💖",
        description='You’ve received a limited-time gift! 🎁\nBe sure to claim it soon! ⏰',
        color=discord.Color.blue()
    )
    embed.set_footer(text="Check your mailbox! When you redeem, you will receive a reward.")
    embed.set_thumbnail(url="https://files.catbox.moe/3kgnjk.png") 

    try:
        await user.send(embed=embed, view=CodeView(code_url))
        print(f"✅ ส่งโค้ดให้ {player_name} แล้ว")
        return True
    except discord.Forbidden:
        print(f"❌ ส่ง DM ให้ {player_name} ไม่ได้ (user id: {user.id})")
        return False
    except Exception as e:
        print(f"❌ Error DM {player_name}: {e}")
        return False

@bot.tree.command(name="sendcode", description="ส่งโค้ด (แบบการ์ด) ให้ทุกคนใน list")
@app_commands.describe(code="โค้ดที่ต้องการส่ง")
async def send_code(interaction: discord.Interaction, code: str):
    await interaction.response.send_message(f"📨 เริ่มส่ง Embed code `{code}` ไปยังผู้ใช้ในรายการ...", ephemeral=True)

    sent = 0
    failed = 0

    for entry in users_send:
        try:
            user = await bot.fetch_user(entry["dis_id"])
            success = await send_code_card_dm(user, code, entry["name"], entry["mid"])
            if success:
                sent += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error ส่งหา {entry['name']} ({entry['dis_id']}): {e}")
            failed += 1

    await interaction.followup.send(
        f"✅ ส่งสำเร็จ {sent} คน | ❌ ล้มเหลว {failed} คน", ephemeral=True
    )


async def send_code_7k_dm(user: discord.User, code: str, player_name: str, mid: str):
    code_url = f"https://coupon.netmarble.com/tskgb?playerId={mid}&code={code}"

    embed = discord.Embed(
        title=f"🥳 {player_name} Guess what? Your surprise gift is here! 🎁💖",
        description='You’ve received a limited-time gift! 🎁\nBe sure to claim it soon! ⏰',
        color=discord.Color.blue()
    )
    embed.set_footer(text="Check your mailbox! When you redeem, you will receive a reward.")
    embed.set_thumbnail(url="https://files.catbox.moe/ff91jz.png") 

    try:
        await user.send(embed=embed, view=CodeView(code_url))
        print(f"✅ ส่งโค้ดให้ {player_name} แล้ว")
        return True
    except discord.Forbidden:
        print(f"❌ ส่ง DM ให้ {player_name} ไม่ได้ (user id: {user.id})")
        return False
    except Exception as e:
        print(f"❌ Error DM {player_name}: {e}")
        return False

@bot.tree.command(name="sendcode", description="ส่งโค้ด (แบบการ์ด) ให้ทุกคนใน list")
@app_commands.describe(code="โค้ดที่ต้องการส่ง")
async def send_code(interaction: discord.Interaction, code: str):
    await interaction.response.send_message(f"📨 เริ่มส่ง Embed code `{code}` ไปยังผู้ใช้ในรายการ...", ephemeral=True)

    sent = 0
    failed = 0

    for entry in users7k_send:
        try:
            user = await bot.fetch_user(entry["dis_id"])
            success = await send_code_7k_dm(user, code, entry["name"], entry["mid"])
            if success:
                sent += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error ส่งหา {entry['name']} ({entry['dis_id']}): {e}")
            failed += 1

    await interaction.followup.send(
        f"✅ ส่งสำเร็จ {sent} คน | ❌ ล้มเหลว {failed} คน", ephemeral=True
    )

bot.run(TOKEN)
