import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .database.db import init_db, add_admin_user
from .utils.helpers import create_backup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Get bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided. Please set it in the .env file.")

# Get admin IDs from environment variables
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS if admin_id.strip()]

# Get backup settings
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", "24"))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler()

async def scheduled_backup():
    """Create scheduled backup."""
    try:
        db_path = os.path.abspath(os.getenv("DATABASE_URL", "app/database/bot_database.db").replace("sqlite:///", ""))
        backup_info = create_backup(db_path, BACKUP_DIR)
        
        # Log backup
        logging.info(f"Scheduled backup created: {backup_info['filename']}")
        
        # Add backup to database
        from .database.db import get_db
        from .database.models import Backup
        
        db = next(get_db())
        backup = Backup(
            filename=backup_info['filename'],
            size=backup_info['size'],
            is_auto=True
        )
        db.add(backup)
        db.commit()
    except Exception as e:
        logging.error(f"Error creating scheduled backup: {e}")

async def on_startup():
    """Actions to perform on bot startup."""
    # Initialize database
    init_db()
    
    # Add admin users
    for admin_id in ADMIN_IDS:
        add_admin_user(admin_id)
    
    # Set bot commands
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help"),
        BotCommand(command="upload", description="Upload a file"),
        BotCommand(command="myfiles", description="View your files"),
        BotCommand(command="search", description="Search for files"),
        BotCommand(command="settings", description="Change settings"),
        BotCommand(command="language", description="Change language"),
        BotCommand(command="myref", description="Your referral link"),
        BotCommand(command="cancel", description="Cancel current operation"),
    ]
    
    await bot.set_my_commands(commands)
    
    # Schedule backups
    scheduler.add_job(scheduled_backup, 'interval', hours=BACKUP_INTERVAL)
    scheduler.start()
    
    # Log startup
    logging.info(f"Bot started at {datetime.now()}")

async def on_shutdown():
    """Actions to perform on bot shutdown."""
    # Close storage
    await storage.close()
    
    # Shutdown scheduler
    scheduler.shutdown()
    
    # Log shutdown
    logging.info(f"Bot stopped at {datetime.now()}")

async def main():
    """Main function to start the bot."""
    # Register handlers
    from .handlers import (
        register_user_handlers,
        register_admin_handlers,
        register_file_handlers,
        register_search_handlers,
        register_callback_handlers
    )
    
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_file_handlers(dp)
    register_search_handlers(dp)
    register_callback_handlers(dp)
    
    # Start the bot
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())