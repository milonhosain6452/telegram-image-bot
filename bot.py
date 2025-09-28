import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image, ImageFilter
import io

# Bot configuration from environment variables
API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8285636468:AAFPRQ1oS1N3I4MBI85RFEOZXW4pwBrWHLg"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'হ্যালো! আমি একটি ইমেজ ব্লার বট।\n\n'
        'আমাকে একটি ইমেজ পাঠান এবং আমি এটিকে মাঝারি পরিমাণে ব্লার করে দেব।\n\n'
        'ইমেজটি খুব বেশি ব্লার হবে না যে বোঝা যাবে না, আবার খুব কমও হবে না যে স্পষ্ট দেখা যাবে।'
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'এই বটটি ইমেজ ব্লার করতে ব্যবহার করা হয়।\n\n'
        'শুধু একটি ইমেজ পাঠান এবং বটটি সেটিকে মাঝারি পরিমাণে ব্লার করে দেবে।\n\n'
        'কমান্ড:\n'
        '/start - বট শুরু করুন\n'
        '/help - সাহায্য দেখুন'
    )

def blur_image(image_data: bytes, blur_radius: int = 3) -> bytes:
    """
    Apply blur effect to an image with specified blur radius.
    
    Args:
        image_data: Image data in bytes
        blur_radius: Radius for Gaussian blur (default: 3)
    
    Returns:
        Blurred image data in bytes
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply Gaussian blur
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Save to bytes
        output_buffer = io.BytesIO()
        blurred_image.save(output_buffer, format='JPEG', quality=85)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise

async def handle_image(update: Update, context: CallbackContext) -> None:
    """Handle incoming images and apply blur effect."""
    try:
        # Send "processing" message
        processing_message = await update.message.reply_text("ইমেজ প্রসেস করা হচ্ছে...")
        
        # Get the photo
        photo_file = await update.message.photo[-1].get_file()
        
        # Download photo data
        photo_data = await photo_file.download_as_bytearray()
        
        # Apply blur effect (blur radius 3 - moderate blur)
        blurred_data = blur_image(bytes(photo_data), blur_radius=3)
        
        # Send the blurred image
        await update.message.reply_photo(
            photo=io.BytesIO(blurred_data),
            caption="ব্লার করা ইমেজ 🎭"
        )
        
        # Delete processing message
        await processing_message.delete()
        
    except Exception as e:
        logger.error(f"Error handling image: {e}")
        await update.message.reply_text("দুঃখিত, ইমেজ প্রসেস করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

async def handle_document(update: Update, context: CallbackContext) -> None:
    """Handle image documents."""
    try:
        document = update.message.document
        
        # Check if it's an image file
        if document.mime_type and document.mime_type.startswith('image/'):
            processing_message = await update.message.reply_text("ইমেজ প্রসেস করা হচ্ছে...")
            
            # Download document
            file = await document.get_file()
            document_data = await file.download_as_bytearray()
            
            # Apply blur effect
            blurred_data = blur_image(bytes(document_data), blur_radius=3)
            
            # Send blurred image
            await update.message.reply_photo(
                photo=io.BytesIO(blurred_data),
                caption="ব্লার করা ইমেজ 🎭"
            )
            
            await processing_message.delete()
        else:
            await update.message.reply_text("দয়া করে একটি ইমেজ ফাইল পাঠান।")
    
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("দুঃখিত, ফাইল প্রসেস করতে সমস্যা হয়েছে।")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    # Start the Bot
    print("বটটি শুরু হয়েছে...")
    application.run_polling()

if __name__ == '__main__':
    main()
