import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image, ImageFilter
import io

# Environment variables - এখানে সরাসরি সেট করে দিচ্ছি
API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8285636468:AAFPRQ1oS1N3I4MBI85RFEOZXW4pwBrWHLg"

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """বট শুরু করার কমান্ড"""
    await update.message.reply_text(
        "স্বাগতম! আমি একটি ইমেজ ব্লারিং বট।\n\n"
        "আমাকে একটি ছবি পাঠান এবং আমি এটিকে মাঝারি পরিমাণে ব্লার করে দেব।"
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """হেল্প কমান্ড"""
    await update.message.reply_text(
        "ব্যবহার নির্দেশিকা:\n"
        "1. আমাকে একটি ছবি পাঠান\n"
        "2. আমি ছবিটি মাঝারি পরিমাণে ব্লার করে আপনাকে ফেরত দেব\n"
        "3. ব্লার পরিমাণ এমন হবে না যে খুব বেশি বা খুব কম"
    )

def apply_blur(image_data):
    """ইমেজে ব্লার ইফেক্ট প্রয়োগ করে"""
    try:
        # ইমেজ খোলা
        image = Image.open(io.BytesIO(image_data))
        
        # ইমেজকে RGB এ কনভার্ট করা (যদি PNG বা অন্য ফরম্যাট হয়)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # মাঝারি পরিমাণে ব্লার প্রয়োগ (রেডিয়াস 5-8 এর মধ্যে)
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius=6))
        
        # ব্লার করা ইমেজকে বাইটে কনভার্ট করা
        output_buffer = io.BytesIO()
        blurred_image.save(output_buffer, format='JPEG', quality=85)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    
    except Exception as e:
        logger.error(f"ইমেজ প্রসেসিং এরর: {e}")
        raise

async def handle_photo(update: Update, context: CallbackContext) -> None:
    """ছবি প্রসেস করার হ্যান্ডলার"""
    try:
        # ইউজারকে জানানো যে কাজ চলছে
        processing_message = await update.message.reply_text("ছবি প্রসেস করা হচ্ছে...")
        
        # সর্বোচ্চ রেজোলিউশনের ছবি ডাউনলোড করা
        photo_file = await update.message.photo[-1].get_file()
        photo_data = await photo_file.download_as_bytearray()
        
        # ব্লার প্রয়োগ
        blurred_photo = apply_blur(photo_data)
        
        # প্রসেসিং মেসেজ ডিলিট করা
        await processing_message.delete()
        
        # ব্লার করা ছবি পাঠানো
        await update.message.reply_photo(
            photo=io.BytesIO(blurred_photo),
            caption="ব্লার করা ছবি 📸"
        )
        
        logger.info(f"ছবি সফলভাবে প্রসেস করা হয়েছে user_id: {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"ছবি প্রসেস করতে সমস্যা: {e}")
        await update.message.reply_text("দুঃখিত, ছবি প্রসেস করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

async def handle_document(update: Update, context: CallbackContext) -> None:
    """ডকুমেন্ট হিসেবে ছবি হ্যান্ডল করা"""
    try:
        document = update.message.document
        
        # শুধু ইমেজ ফাইল এক্সটেনশন চেক করা
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        file_extension = os.path.splitext(document.file_name or '')[-1].lower()
        
        if file_extension not in allowed_extensions:
            await update.message.reply_text("দুঃখিত, শুধুমাত্র ইমেজ ফাইল সাপোর্টেড (JPG, PNG, BMP, GIF)")
            return
        
        # ফাইল সাইজ চেক (10MB এর কম)
        if document.file_size > 10 * 1024 * 1024:
            await update.message.reply_text("দুঃখিত, ফাইল সাইজ 10MB এর কম হতে হবে")
            return
        
        # ইউজারকে জানানো যে কাজ চলছে
        processing_message = await update.message.reply_text("ছবি প্রসেস করা হচ্ছে...")
        
        # ফাইল ডাউনলোড করা
        document_file = await document.get_file()
        document_data = await document_file.download_as_bytearray()
        
        # ব্লার প্রয়োগ
        blurred_image = apply_blur(document_data)
        
        # প্রসেসিং মেসেজ ডিলিট করা
        await processing_message.delete()
        
        # ব্লার করা ছবি পাঠানো
        await update.message.reply_document(
            document=io.BytesIO(blurred_image),
            filename=f"blurred_image{file_extension}",
            caption="ব্লার করা ছবি 📸"
        )
        
        logger.info(f"ডকুমেন্ট ইমেজ সফলভাবে প্রসেস করা হয়েছে user_id: {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"ডকুমেন্ট প্রসেস করতে সমস্যা: {e}")
        await update.message.reply_text("দুঃখিত, ফাইল প্রসেস করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

async def error_handler(update: Update, context: CallbackContext) -> None:
    """এরর হ্যান্ডলার"""
    logger.error(f"আপডেট {update} এর কারণে এরর: {context.error}")

def main() -> None:
    """বট শুরু করা"""
    try:
        # বট অ্যাপ্লিকেশন তৈরি
        application = Application.builder().token(BOT_TOKEN).build()
        
        # কমান্ড হ্যান্ডলার
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # ফটো হ্যান্ডলার
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # ডকুমেন্ট হ্যান্ডলার (ইমেজ ফাইল)
        application.add_handler(MessageHandler(
            filters.Document.IMAGE | 
            filters.Document.MIME_TYPE("image/jpeg") |
            filters.Document.MIME_TYPE("image/png") |
            filters.Document.MIME_TYPE("image/bmp") |
            filters.Document.MIME_TYPE("image/gif"),
            handle_document
        ))
        
        # এরর হ্যান্ডলার
        application.add_error_handler(error_handler)
        
        # বট শুরু করা
        print("বট শুরু হচ্ছে...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"বট শুরু করতে সমস্যা: {e}")

if __name__ == '__main__':
    main()
