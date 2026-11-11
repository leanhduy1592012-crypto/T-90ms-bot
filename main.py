import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask
from google import genai

# --- 1. WEB SERVER GIẢ LẬP ĐỂ GIỮ CỔNG RENDER (TRÁNH LỖI PORT TIMEOUT) ---
app = Flask('')


@app.route('/')
def home():
  return 'Bot T-90MS đang hoạt động 24/7!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


# Chạy server web ngầm
keep_alive()

# --- 2. CẤU HÌNH NHÂN CÁCH & BOT T-90MS ---
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Khởi tạo Gemini Client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# System Instruction định hình phong cách "Chỉ huy Quân sự" cho T-90MS
SYSTEM_INSTRUCTION = """
Bạn là T-90MS, một Chỉ huy Quân sự cứng rắn, quyết đoán và tuân thủ kỷ luật tuyệt đối trên server Discord.
Phong cách giao tiếp:
- Xưng hô: "Chỉ huy" (hoặc "Tôi") và gọi người dùng là "Đồng chí" hoặc gọi tên của họ.
- Giọng văn: Ngắn gọn, đanh thép, tác phong quân đội, hướng tới giải quyết vấn đề nhanh gọn.
- Nhiệm vụ: Hỗ trợ quản lý server, xử lý tranh chấp, đưa ra mệnh lệnh rõ ràng. Không nói lảm nhảm, không dùng từ ngữ thừa thãi.
"""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  print(f'========================================')
  print(f'   T-90MS ĐÃ NỔ MÁY VÀ VÀO VỊ TRÍ TRÊN MÂY!')
  print(f'   Bot Username: {bot.user}')
  print(f'========================================')


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  # Khi được tag tên hoặc nhắn tin riêng (DM)
  if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
    clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()

    if not clean_content:
      await message.channel.send(
          f'**[T-90MS]** Báo cáo tình hình đi, đồng chí {message.author.mention}!'
      )
      return

    async with message.channel.typing():
      try:
        # Đã cập nhật lên model gemini-3.8-flash mới nhất
        response = gemini_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=clean_content,
            config={
                'system_instruction': SYSTEM_INSTRUCTION,
            },
        )
        reply_text = response.text

        if len(reply_text) > 2000:
          reply_text = reply_text[:1997] + '...'

        await message.reply(reply_text)
      except Exception as e:
        await message.reply(f'**[T-90MS]** Lỗi hệ thống truyền tin: `{e}`')

  await bot.process_commands(message)


if __name__ == '__main__':
  bot.run(DISCORD_TOKEN)
