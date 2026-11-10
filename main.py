import os
import discord
from discord.ext import commands
from google import genai

# Khởi tạo kết nối bảo mật từ biến môi trường trên Render
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
Bạn là T-90MS, một Chỉ huy Quân sự cứng rắn, quyết đoán và tuân thủ kỷ luật tuyệt đối trên server Discord.
Phong cách giao tiếp:
- Xưng hô: "Chỉ huy" (hoặc "Tôi") và gọi người dùng là "Đồng chí" hoặc gọi tên của họ.
- Giọng văn: Ngắn gọn, đanh thép, tác phong quân đội, hướng tới giải quyết vấn đề nhanh gọn.
- Nhiệm vụ: Hỗ trợ quản lý server, xử lý tranh chấp, đưa ra mệnh lệnh rõ ràng. Không nói lảm nhảm, không dùng từ ngữ thừa thãi.
"""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"==========================================")
    print(f"  T-90MS SKST ĐÃ NỔ MÁY VÀ VÀO VỊ TRÍ TRÊN MÂY!")
    print(f"  Bot Username: {bot.user}")
    print(f"==========================================")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not clean_content:
            await message.channel.send(f"**[T-90MS]** Báo cáo tình hình đi, đồng chí {message.author.mention}!")
            return

        async with message.channel.typing():
            try:
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=clean_content,
                    config={
                        'system_instruction': SYSTEM_INSTRUCTION,
                        'temperature': 0.5,
                    }
                )
                reply_text = response.text.strip()
                await message.channel.send(f"{message.author.mention} {reply_text}")
            except Exception as e:
                print(f"Lỗi khi xử lý lệnh AI: {e}")
                await message.channel.send(f"**[T-90MS]** Hệ thống liên lạc bị nhiễu sóng! Báo cáo lỗi kỹ thuật.")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)