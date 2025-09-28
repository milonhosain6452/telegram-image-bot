#!/usr/bin/env python3
"""
Telegram Blur Bot
A bot that applies moderate blur effects to images sent by users.
"""

import os
import logging
import asyncio
from typing import Optional
from PIL import Image, ImageFilter
from pyrogram import Client, filters
from pyrogram.types import Message
import tempfile
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot credentials
API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8285636468:AAFPRQ1oS1N3I4MBI85RFEOZXW4pwBrWHLg"

class TelegramBlurBot:
    def __init__(self):
        """Initialize the Telegram Blur Bot."""
        self.app = Client(
            "blur_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )
        
        # Create temp directory for processing
        self.temp_dir = "/home/sandbox/telegram_blur_bot/temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Register handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register message handlers."""
        self.app.on_message(filters.command("start"))(self.start_command)
        self.app.on_message(filters.command("help"))(self.help_command)
        self.app.on_message(filters.photo & filters.private)(self.handle_photo)
        self.app.on_message(filters.document & filters.private)(self.handle_document)
        self.app.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))(self.handle_text)
    
    async def start_command(self, client: Client, message: Message):
        """Handle /start command."""
        welcome_text = """
🌟 **Welcome to Blur Bot!** 🌟

I can apply a moderate blur effect to your images while keeping them recognizable.

**How to use:**
1. Send me any image (photo or document)
2. I'll process it and send back the blurred version
3. The blur effect obscures details but maintains recognizability

**Supported formats:** JPG, PNG, WEBP, BMP, TIFF

Just send me an image to get started! 📸✨
        """
        await message.reply_text(welcome_text)
    
    async def help_command(self, client: Client, message: Message):
        """Handle /help command."""
        help_text = """
🔧 **Blur Bot Help** 🔧

**Commands:**
• `/start` - Show welcome message
• `/help` - Show this help message

**Usage:**
• Send any image as a photo or document
• I'll apply a moderate blur effect
• You'll receive the blurred image back

**Features:**
• Fast processing ⚡
• Maintains image quality 📸
• Works with various formats 🖼️
• Private chat only 🔒

**Tips:**
• Larger images may take a bit longer to process
• The blur effect is designed to obscure details while keeping the image recognizable
        """
        await message.reply_text(help_text)
    
    async def handle_text(self, client: Client, message: Message):
        """Handle text messages."""
        await message.reply_text(
            "Please send me an image to apply blur effect! 📸\n\n"
            "You can send images as photos or documents."
        )
    
    async def handle_photo(self, client: Client, message: Message):
        """Handle photo messages."""
        await self.process_image(client, message, is_photo=True)
    
    async def handle_document(self, client: Client, message: Message):
        """Handle document messages (for image files)."""
        if not message.document:
            return
        
        # Check if document is an image
        mime_type = message.document.mime_type or ""
        if not mime_type.startswith("image/"):
            await message.reply_text(
                "Please send image files only! 🖼️\n\n"
                "Supported formats: JPG, PNG, WEBP, BMP, TIFF"
            )
            return
        
        await self.process_image(client, message, is_photo=False)
    
    async def process_image(self, client: Client, message: Message, is_photo: bool):
        """Process and blur the image."""
        try:
            # Send processing message
            processing_msg = await message.reply_text("🔄 Processing your image...")
            
            # Create unique filename
            timestamp = str(int(time.time()))
            user_id = message.from_user.id
            
            # Download the image
            if is_photo:
                file_path = await message.download(
                    file_name=f"{self.temp_dir}/input_{user_id}_{timestamp}.jpg"
                )
            else:
                file_path = await message.download(
                    file_name=f"{self.temp_dir}/input_{user_id}_{timestamp}_{message.document.file_name}"
                )
            
            logger.info(f"Downloaded image: {file_path}")
            
            # Apply blur effect
            blurred_path = await self.apply_blur_effect(file_path, user_id, timestamp)
            
            # Update processing message
            await processing_msg.edit_text("📤 Sending blurred image...")
            
            # Send the blurred image
            await message.reply_photo(
                photo=blurred_path,
                caption="✨ **Blurred Image Ready!** ✨\n\nYour image has been processed with a moderate blur effect."
            )
            
            # Clean up files
            self.cleanup_files([file_path, blurred_path])
            
            # Delete processing message
            await processing_msg.delete()
            
            logger.info(f"Successfully processed image for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            await message.reply_text(
                "❌ **Error processing image!**\n\n"
                "Please try again with a different image or contact support if the problem persists."
            )
    
    async def apply_blur_effect(self, input_path: str, user_id: int, timestamp: str) -> str:
        """Apply moderate blur effect to the image."""
        try:
            # Open the image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Convert to RGB, handling transparency
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Apply moderate blur effect
                # Using Gaussian blur with radius 3 for moderate effect
                blurred_img = img.filter(ImageFilter.GaussianBlur(radius=3))
                
                # Generate output path
                output_path = f"{self.temp_dir}/blurred_{user_id}_{timestamp}.jpg"
                
                # Save with good quality
                blurred_img.save(output_path, 'JPEG', quality=85, optimize=True)
                
                logger.info(f"Applied blur effect: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error applying blur effect: {str(e)}")
            raise
    
    def cleanup_files(self, file_paths: list):
        """Clean up temporary files."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up file {file_path}: {str(e)}")
    
    async def run(self):
        """Start the bot."""
        logger.info("Starting Telegram Blur Bot...")
        await self.app.start()
        logger.info("Bot started successfully!")
        
        # Keep the bot running
        await asyncio.Event().wait()

async def main():
    """Main function to run the bot."""
    bot = TelegramBlurBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
    finally:
        await bot.app.stop()

if __name__ == "__main__":
    asyncio.run(main())
