# -*- coding: utf-8 -*-
import os
import io
from telegram import Update, File
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image, ImageFilter

# আপনার দেওয়া ডিটেইলস (ENV Variables)
# NOTE: নিরাপত্তার জন্য, সাধারণত এই key/value গুলো সরাসরি কোডে রাখা উচিত নয়।
# Render-এর জন্য আপনি Environment Variables ব্যবহার করতে পারেন,
# তবে আপনার অনুরোধ অনুযায়ী আমি কোডেই দিয়ে দিচ্ছি।
API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8285636468:AAFPRQ1oS1N3I4MBI85RFEOZXW4pwBrWHLg"

# Gaussian Blur এর জন্য ব্লার এর মাত্রা (Radius)।
# 5.0 একটি মাঝারি মানের ব্লার দেয়, যা আপনার চাহিদা (বোঝা যাবে না আবার এতো কমও হবে না) পূরণের জন্য উপযুক্ত।
BLUR_RADIUS = 5.0 

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """বট শুরু হলে /start কমান্ডের উত্তর দেয়।"""
    await update.message.reply_text(
        "👋 নমস্কার! আমি আপনার ইমেজ ব্লার বট। আমাকে একটি ছবি পাঠান, আমি এটিকে হালকা ব্লার করে ফেরত দেবো।\n"
        "আমার ব্লার এর মাত্রা: {BLUR_RADIUS}"
    )

async def blur_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ইউজারের পাঠানো ছবি ডাউনলোড করে, ব্লার করে এবং ব্লার করা ছবি ফেরত পাঠায়।"""
    chat_id = update.message.chat_id
    
    # 1. ছবি ডাউনলোড করা
    try:
        # টেলিগ্রাম থেকে ছবির সবচেয়ে বড় সাইজের ফাইলটি নেওয়া
        photo_file_id = update.message.photo[-1].file_id
        new_file: File = await context.bot.get_file(photo_file_id)
        
        # ফাইলটিকে মেমরিতে ডাউনলোড করা 
        # (Render-এ ফাইল সিস্টেমে সেভ না করে মেমরিতে কাজ করা ভালো)
        image_data = await new_file.download_as_bytes()
        
    except Exception as e:
        await update.message.reply_text("ছবি ডাউনলোডে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।")
        print(f"Error downloading image: {e}")
        return

    await update.message.reply_text("ছবিটি পেয়েছি। ব্লার করছি... ⏳")

    # 2. ছবি এডিট করে ব্লার করা
    try:
        # বাইট ডেটা থেকে PIL ইমেজ অবজেক্ট তৈরি করা
        original_image = Image.open(io.BytesIO(image_data))
        
        # Gaussian Blur প্রয়োগ করা 
        # GaussianBlur সাধারণত ভালো, প্রাকৃতিক ব্লার এফেক্ট দেয়।
        blurred_image = original_image.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))

        # ব্লার করা ছবিটি সেভ করার জন্য একটি মেমরি বাফার তৈরি করা
        buffered_output = io.BytesIO()
        # ছবির আসল ফরম্যাট বজায় রাখতে original_image.format ব্যবহার করা উচিত, তবে 
        # JPEG ব্যবহার করা হলো যাতে সব ঠিক থাকে। PNG/GIF-এর ক্ষেত্রেও সেভ করা যেতে পারে।
        if original_image.mode in ('RGBA', 'P'):
            # ট্রান্সপারেন্সি থাকলে PNG ব্যবহার করা
            blurred_image.save(buffered_output, format="PNG")
        else:
            blurred_image.save(buffered_output, format="JPEG")
            
        buffered_output.seek(0)
        
    except Exception as e:
        await update.message.reply_text("ছবি ব্লার করার সময় একটি সমস্যা হয়েছে। ❌")
        print(f"Error processing image: {e}")
        return
        
    # 3. ব্লার করা ছবি ফেরত পাঠানো
    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=buffered_output,
            caption=f"ছবিটি সফলভাবে ব্লার করা হয়েছে (Radius: {BLUR_RADIUS})। ✅"
        )
    except Exception as e:
        await update.message.reply_text("ব্লার করা ছবি পাঠাতে সমস্যা হয়েছে।")
        print(f"Error sending blurred image: {e}")


def main() -> None:
    """বট শুরু করে।"""
    # Application তৈরি করা
    application = Application.builder().token(BOT_TOKEN).build()

    # কমান্ড এবং মেসেজ হ্যান্ডলার যোগ করা
    application.add_handler(CommandHandler("start", start_command))
    # 'photo' কন্টেন্ট টাইপের মেসেজগুলোর জন্য হ্যান্ডলার
    application.add_handler(MessageHandler(filters.PHOTO, blur_image))

    # বটকে চালু রাখা 
    # Render-এ Webhook ব্যবহার করা সবচেয়ে ভালো, কিন্তু সহজতম উপায়ের জন্য Polling ব্যবহার করা হলো।
    # আপনি Webhook-এর জন্য কোডটি পরিবর্তন করতে পারেন যদি আপনার প্রয়োজন হয়।
    print("বট চালু হচ্ছে... Polling শুরু হলো।")
    application.run_polling(poll_interval=3)

if __name__ == "__main__":
    # CommandHandler-কে main-এর বাইরে ডিফাইন করা হয়, তাই এটিকে এখানে ইম্পোর্ট করতে হবে।
    from telegram.ext import CommandHandler
    main()
