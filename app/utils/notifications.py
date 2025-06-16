"""
Notification utilities for the bot.
"""
import logging
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from aiogram import Bot

from ..database.models import User, File, Notification

async def send_notification_to_user(bot: Bot, user_id: int, message: str) -> bool:
    """Send notification to a user."""
    try:
        await bot.send_message(chat_id=user_id, text=message)
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {user_id}: {e}")
        return False

async def send_notification_to_users(bot: Bot, user_ids: List[int], message: str) -> int:
    """Send notification to multiple users."""
    success_count = 0
    for user_id in user_ids:
        if await send_notification_to_user(bot, user_id, message):
            success_count += 1
    return success_count

async def send_notification_to_all_users(bot: Bot, db: Session, message: str) -> int:
    """Send notification to all users."""
    users = db.query(User).all()
    user_ids = [user.telegram_id for user in users]
    return await send_notification_to_users(bot, user_ids, message)

async def send_notification_to_active_users(bot: Bot, db: Session, message: str, days: int = 7) -> int:
    """Send notification to active users."""
    from .helpers import get_active_users
    active_users = get_active_users(db, days)
    user_ids = [user.telegram_id for user in active_users]
    return await send_notification_to_users(bot, user_ids, message)

async def send_file_download_notification(bot: Bot, db: Session, file_id: int, downloader_id: int) -> bool:
    """Send notification to file owner when someone downloads their file."""
    # Get file
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        return False
    
    # Get file owner
    owner = db.query(User).filter(User.id == file.owner_id).first()
    
    if not owner:
        return False
    
    # Get downloader
    downloader = db.query(User).filter(User.telegram_id == downloader_id).first()
    
    if not downloader:
        return False
    
    # Create notification message
    downloader_name = downloader.username or f"{downloader.first_name or ''} {downloader.last_name or ''}".strip() or f"User {downloader.telegram_id}"
    message = f"📥 Your file '{file.file_name}' was downloaded by {downloader_name}."
    
    # Store notification in database
    notification = Notification(
        user_id=owner.id,
        message=message,
        is_read=False,
        notification_type="file_download"
    )
    db.add(notification)
    db.commit()
    
    # Send notification
    return await send_notification_to_user(bot, owner.telegram_id, message)

async def send_system_notification(bot: Bot, db: Session, message: str, notification_type: str = "system") -> int:
    """Send system notification to all admin users."""
    # Get admin users
    admin_users = db.query(User).filter(User.is_admin == True).all()
    
    if not admin_users:
        return 0
    
    # Store notification in database for each admin
    for admin in admin_users:
        notification = Notification(
            user_id=admin.id,
            message=message,
            is_read=False,
            notification_type=notification_type
        )
        db.add(notification)
    
    db.commit()
    
    # Send notification to admins
    admin_ids = [admin.telegram_id for admin in admin_users]
    return await send_notification_to_users(bot, admin_ids, message)

def get_user_notifications(db: Session, user_id: int, unread_only: bool = False, limit: int = 10) -> List[Notification]:
    """Get notifications for a user."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return query.order_by(Notification.created_at.desc()).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int) -> bool:
    """Mark a notification as read."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        return False
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return True

def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """Mark all notifications as read for a user."""
    result = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({
        Notification.is_read: True,
        Notification.read_at: datetime.utcnow()
    })
    
    db.commit()
    
    return result