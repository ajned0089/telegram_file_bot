import os
import logging
import secrets
import string
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from aiogram import Bot

from ..database.models import User, File, Category, Format, Tag, FileDownload, SubscriptionChannel

def get_or_create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None, language_code: str = "en") -> User:
    """Get or create a user."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        # Create new user
        referral_code = f"ref_{secrets.token_hex(8)}"
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referral_code=referral_code
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user information
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.last_activity = datetime.utcnow()
        db.commit()
    
    return user

def get_user_language(telegram_id: int, db: Session) -> str:
    """Get user language."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        # Default to English
        return "en"
    
    return user.language_code

def is_admin(telegram_id: int, db: Session) -> bool:
    """Check if user is admin."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        return False
    
    return user.is_admin

def can_upload(telegram_id: int, db: Session) -> bool:
    """Check if user can upload files."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        return False
    
    # Check if user is banned
    if user.is_banned:
        return False
    
    # Check if user is admin or moderator
    if user.is_admin or user.is_moderator:
        return True
    
    # Check if public upload is allowed
    from ..database.db import get_setting
    allow_public_upload = get_setting(db, "allow_public_upload", "true")
    
    if allow_public_upload.lower() == "true":
        return user.can_upload
    
    return False

async def check_subscription(telegram_id: int, bot: Bot, db: Session) -> bool:
    """Check if user is subscribed to required channels."""
    # Get required channels
    channels = db.query(SubscriptionChannel).filter(SubscriptionChannel.is_required == True).all()
    
    if not channels:
        return True
    
    for channel in channels:
        try:
            # Check if user is a member of the channel
            member = await bot.get_chat_member(channel.channel_id, telegram_id)
            
            # Check if user is a member (not left or kicked)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"Error checking subscription: {e}")
            # If there's an error, assume user is not subscribed
            return False
    
    return True

def get_subscription_buttons(db: Session, lang: str):
    """Get subscription buttons."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from ..localization.strings import get_string
    
    # Get required channels
    channels = db.query(SubscriptionChannel).filter(SubscriptionChannel.is_required == True).all()
    
    if not channels:
        return None
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        builder.button(text=channel.channel_name, url=channel.channel_link)
    
    builder.button(text=get_string("check_subscription", lang), callback_data="check_subscription")
    builder.adjust(1)
    
    return builder.as_markup()

def get_file_size_str(size_in_bytes: int) -> str:
    """Convert file size in bytes to human-readable format."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

def generate_share_link(bot_username: str, share_code: str) -> str:
    """Generate share link for file."""
    return f"https://t.me/{bot_username}?start=file_{share_code}"

def parse_tags(tags_text: str) -> List[str]:
    """Parse tags from text."""
    if not tags_text:
        return []
    
    # Split by commas or spaces
    tags = []
    for tag in tags_text.split(","):
        tag = tag.strip()
        if tag:
            tags.append(tag)
    
    return tags

def get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    """Get or create tags."""
    tags = []
    
    for tag_name in tag_names:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        
        tags.append(tag)
    
    return tags

def get_file_by_share_code(db: Session, share_code: str) -> Optional[File]:
    """Get file by share code."""
    return db.query(File).filter(File.share_code == share_code).first()

def update_file_stats(db: Session, file_id: int, is_download: bool = False, is_view: bool = False) -> None:
    """Update file statistics."""
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        return
    
    if is_download:
        file.download_count += 1
    
    if is_view:
        file.view_count += 1
    
    db.commit()

def add_file_download(db: Session, file_id: int, telegram_id: int) -> None:
    """Add file download record."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        return
    
    # Check if download record already exists
    download = db.query(FileDownload).filter(
        FileDownload.file_id == file_id,
        FileDownload.user_id == user.id
    ).first()
    
    if download:
        # Update existing record
        download.download_count += 1
        download.last_download = datetime.utcnow()
    else:
        # Create new record
        download = FileDownload(
            file_id=file_id,
            user_id=user.id,
            download_count=1
        )
        db.add(download)
    
    db.commit()

def get_user_files(db: Session, telegram_id: int) -> List[File]:
    """Get files uploaded by user."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        return []
    
    return db.query(File).filter(File.owner_id == user.id).all()

def search_files_by_name(db: Session, query: str) -> List[File]:
    """Search files by name."""
    return db.query(File).filter(File.file_name.ilike(f"%{query}%")).all()

def search_files_by_tag(db: Session, query: str) -> List[File]:
    """Search files by tag."""
    tag = db.query(Tag).filter(Tag.name.ilike(f"%{query}%")).first()
    
    if not tag:
        return []
    
    return tag.files

def search_files_by_category(db: Session, category_id: int) -> List[File]:
    """Search files by category."""
    return db.query(File).filter(File.category_id == category_id).all()

def search_files_by_format(db: Session, format_id: int) -> List[File]:
    """Search files by format."""
    return db.query(File).filter(File.format_id == format_id).all()

def get_active_users(db: Session, days: int = 7) -> List[User]:
    """Get active users in the last X days."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return db.query(User).filter(User.last_activity >= cutoff_date).all()

def get_total_storage_used(db: Session) -> str:
    """Get total storage used."""
    total_size = db.query(db.func.sum(File.file_size)).scalar() or 0
    return get_file_size_str(total_size)

def create_backup(db_path: str, backup_dir: str = "backups") -> Dict[str, Any]:
    """Create database backup."""
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = os.path.join(backup_dir, f"backup_{timestamp}.db")
    
    # Copy database file
    shutil.copy2(db_path, backup_filename)
    
    # Get backup file size
    backup_size = os.path.getsize(backup_filename)
    
    return {
        "filename": backup_filename,
        "size": backup_size
    }

def restore_backup(backup_filename: str, db_path: str) -> None:
    """Restore database from backup."""
    # Check if backup file exists
    if not os.path.exists(backup_filename):
        raise FileNotFoundError(f"Backup file not found: {backup_filename}")
    
    # Create backup of current database
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup = f"{db_path}.{timestamp}.bak"
    shutil.copy2(db_path, current_backup)
    
    # Restore backup
    shutil.copy2(backup_filename, db_path)