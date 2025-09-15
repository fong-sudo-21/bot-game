import os
import json
import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- GOOGLE SHEET CONFIG ----------------
SHEET_NAME = os.getenv("SHEET_NAME")
GOOGLE_CRED_JSON = os.getenv("GOOGLE_CRED_JSON")

if not SHEET_NAME or not GOOGLE_CRED_JSON:
    raise ValueError("❌ Chưa cấu hình SHEET_NAME hoặc GOOGLE_CRED_JSON")

# Parse credentials từ biến môi trường (JSON string → dict)
creds_dict = json.loads(GOOGLE_CRED_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # sheet đầu tiên

# ---------------- DISCORD CONFIG ----------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("❌ Chưa cấu hình DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------- COMMANDS ----------------
@bot.event
async def on_ready():
    print(f"✅ Bot đã online: {bot.user}")


# Lệnh tìm game bằng embed
@bot.command(name="find")
async def find_game(ctx, *, game_name: str):
    try:
        records = sheet.get_all_records()
        result = [row for row in records if game_name.lower() in row['Tên Game'].lower()]

        if not result:
            await ctx.send(f"❌ Không tìm thấy game nào tên: **{game_name}**")
        else:
            embed = discord.Embed(
                title=f"🔎 Kết quả tìm kiếm cho: {game_name}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Tìm thấy {len(result)} game")

            for row in result:
                game_name = row['Tên Game']
                game_link = row['Link tải']
                embed.add_field(
                    name=f"🎮 {game_name}",
                    value=f"[Tải tại đây]({game_link})",
                    inline=False
                )

            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Lỗi: {e}")


# Lệnh hiển thị toàn bộ danh sách game bằng embed
@bot.command(name="list")
async def list_games(ctx):
    try:
        records = sheet.get_all_records()

        if not records:
            await ctx.send("❌ Không có dữ liệu.")
            return

        embed = discord.Embed(
            title="📋 Danh sách game hiện có",
            description="Các game và link tải",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Tổng số game: {len(records)}")

        for row in records:
            game_name = row['Tên Game']
            game_link = row['Link tải']
            embed.add_field(
                name=f"🎮 {game_name}",
                value=f"[Tải tại đây]({game_link})",
                inline=False
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠️ Lỗi: {e}")


# Lệnh chọn game ngẫu nhiên
@bot.command(name="random")
async def random_game(ctx):
    import random
    try:
        records = sheet.get_all_records()

        if not records:
            await ctx.send("❌ Không có dữ liệu.")
            return

        row = random.choice(records)
        embed = discord.Embed(
            title="🎲 Game ngẫu nhiên",
            color=discord.Color.purple()
        )
        embed.add_field(
            name=f"🎮 {row['Tên Game']}",
            value=f"[Tải tại đây]({row['Link tải']})",
            inline=False
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠️ Lỗi: {e}")


# ---------------- RUN BOT ----------------
bot.run(DISCORD_TOKEN)

