# bot.py
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageFilter
import io

# ===================== Bot Credentials =====================
API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8285636468:AAFPRQ1oS1N3I4MBI85RFEOZXW4pwBrWHLg"
# ===========================================================

# Bot Initialization
app = Client("blur_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("হ্যালো! আমাকে ইমেজ পাঠাও, আমি সেটি ব্লার করে দিব।")

# Handle incoming images
@app.on_message(filters.photo)
async def blur_image(client, message: Message):
    await message.reply_text("🖌 ব্লার প্রক্রিয়া শুরু হচ্ছে...")

    # Download image into memory
    image_bytes = await message.download(file=io.BytesIO())

    # Open image with PIL
    img = Image.open(image_bytes)

    # Apply moderate blur
    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=5))  # Moderate blur, adjust if needed

    # Save to bytes
    output_bytes = io.BytesIO()
    output_bytes.name = "blurred.png"
    blurred_img.save(output_bytes, format="PNG")
    output_bytes.seek(0)

    # Send back blurred image
    await message.reply_photo(photo=output_bytes, caption="✅ ব্লার করা ইমেজ।")

# Run bot
print("Bot is running...")
app.run()
