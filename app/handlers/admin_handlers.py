from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from datetime import datetime, timedelta

from ..database.db import get_db, update_setting, create_backup, restore_backup
from ..database.models import User, File, Category, Format, SubscriptionChannel, Settings, Backup
from ..utils.states import AdminStates
from ..utils.helpers import (
    get_user_language, is_admin, get_active_users,
    get_total_storage_used, get_file_size_str
)
from ..localization.strings import get_string

router = Router()

async def admin_command(message: Message, state: FSMContext):
    """Handle /admin command."""
    # Get database session
    db = next(get_db())
    
    # Check if user is admin
    if not is_admin(message.from_user.id, db):
        # Get user language
        lang = get_user_language(message.from_user.id, db)
        
        # Send not authorized message
        await message.answer(get_string("not_authorized", lang))
        return
    
    # Set state to admin main menu
    await state.set_state(AdminStates.main_menu)
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Create admin panel keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("user_management", lang), callback_data="admin_users")
    builder.button(text=get_string("category_management", lang), callback_data="admin_categories")
    builder.button(text=get_string("format_management", lang), callback_data="admin_formats")
    builder.button(text=get_string("subscription_management", lang), callback_data="admin_subscriptions")
    builder.button(text=get_string("settings", lang), callback_data="admin_settings")
    builder.button(text=get_string("statistics", lang), callback_data="admin_statistics")
    builder.button(text=get_string("backup", lang), callback_data="admin_backup")
    builder.button(text=get_string("broadcast", lang), callback_data="admin_broadcast")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(2)
    
    # Send admin panel message
    await message.answer(
        f"⚙️ <b>{get_string('admin_panel', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )

async def handle_admin_users(callback: CallbackQuery, state: FSMContext):
    """Handle admin users."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to user management
    await state.set_state(AdminStates.user_management)
    
    # Get recent users
    recent_users = db.query(User).order_by(User.last_activity.desc()).limit(10).all()
    
    # Create user management keyboard
    builder = InlineKeyboardBuilder()
    
    for user in recent_users:
        display_name = user.username or f"{user.first_name or ''} {user.last_name or ''}".strip() or f"User {user.telegram_id}"
        builder.button(text=display_name, callback_data=f"user_{user.id}")
    
    builder.button(text="🔍 Search User", callback_data="search_user")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send user management message
    await callback.message.edit_text(
        f"👥 <b>{get_string('user_management', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_categories(callback: CallbackQuery, state: FSMContext):
    """Handle admin categories."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to category management
    await state.set_state(AdminStates.category_management)
    
    # Get main categories
    categories = db.query(Category).filter(Category.parent_id == None).all()
    
    # Create category management keyboard
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        category_name = category.name_en if lang == "en" else category.name_ar
        status = "✅" if category.is_active else "❌"
        builder.button(text=f"{category_name} {status}", callback_data=f"category_{category.id}")
    
    builder.button(text="➕ Add Category", callback_data="add_category")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send category management message
    await callback.message.edit_text(
        f"📂 <b>{get_string('category_management', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_formats(callback: CallbackQuery, state: FSMContext):
    """Handle admin formats."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to format management
    await state.set_state(AdminStates.format_management)
    
    # Get formats
    formats = db.query(Format).all()
    
    # Create format management keyboard
    builder = InlineKeyboardBuilder()
    
    for format in formats:
        status = "✅" if format.is_active else "❌"
        builder.button(text=f"{format.name} {status}", callback_data=f"format_{format.id}")
    
    builder.button(text="➕ Add Format", callback_data="add_format")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send format management message
    await callback.message.edit_text(
        f"📄 <b>{get_string('format_management', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_subscriptions(callback: CallbackQuery, state: FSMContext):
    """Handle admin subscriptions."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to subscription management
    await state.set_state(AdminStates.subscription_management)
    
    # Get subscription channels
    channels = db.query(SubscriptionChannel).all()
    
    # Create subscription management keyboard
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        status = "✅" if channel.is_required else "❌"
        builder.button(text=f"{channel.channel_name} {status}", callback_data=f"channel_{channel.id}")
    
    builder.button(text="➕ Add Channel", callback_data="add_channel")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send subscription management message
    await callback.message.edit_text(
        f"📢 <b>{get_string('subscription_management', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_settings(callback: CallbackQuery, state: FSMContext):
    """Handle admin settings."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to settings management
    await state.set_state(AdminStates.settings_management)
    
    # Get settings
    settings = db.query(Settings).all()
    
    # Create settings management keyboard
    builder = InlineKeyboardBuilder()
    
    for setting in settings:
        builder.button(text=f"{setting.key}: {setting.value}", callback_data=f"setting_{setting.id}")
    
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send settings management message
    await callback.message.edit_text(
        f"⚙️ <b>{get_string('settings', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_statistics(callback: CallbackQuery, state: FSMContext):
    """Handle admin statistics."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get statistics
    total_users = db.query(User).count()
    total_files = db.query(File).count()
    total_downloads = db.query(db.func.sum(File.download_count)).scalar() or 0
    storage_used = get_total_storage_used(db)
    active_users = len(get_active_users(db, 7))
    
    # Create statistics message
    statistics_message = f"""
📊 <b>{get_string('statistics', lang)}</b>

{get_string('total_users', lang).format(count=total_users)}
{get_string('total_files', lang).format(count=total_files)}
{get_string('total_downloads', lang).format(count=total_downloads)}
{get_string('storage_used', lang).format(size=storage_used)}
{get_string('active_users', lang).format(count=active_users)}
"""
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    
    # Send statistics message
    await callback.message.edit_text(
        statistics_message,
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_backup(callback: CallbackQuery, state: FSMContext):
    """Handle admin backup."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to backup management
    await state.set_state(AdminStates.backup_management)
    
    # Get recent backups
    backups = db.query(Backup).order_by(Backup.created_at.desc()).limit(5).all()
    
    # Create backup management keyboard
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📦 Create Backup", callback_data="create_backup")
    
    for backup in backups:
        backup_date = backup.created_at.strftime("%Y-%m-%d %H:%M")
        backup_size = get_file_size_str(backup.size)
        backup_type = "🔄 Auto" if backup.is_auto else "📦 Manual"
        builder.button(
            text=f"{backup_type} {backup_date} ({backup_size})",
            callback_data=f"backup_{backup.id}"
        )
    
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send backup management message
    await callback.message.edit_text(
        f"💾 <b>{get_string('backup', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Handle admin broadcast."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to broadcast
    await state.set_state(AdminStates.broadcast)
    
    # Create broadcast keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text="📣 Send to All Users", callback_data="broadcast_all")
    builder.button(text="📣 Send to Active Users", callback_data="broadcast_active")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
    builder.adjust(1)
    
    # Send broadcast message
    await callback.message.edit_text(
        f"📣 <b>{get_string('broadcast', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_create_backup(callback: CallbackQuery, state: FSMContext):
    """Handle create backup."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Send creating backup message
    await callback.message.edit_text("⏳ Creating backup...")
    
    try:
        # Get database path
        db_path = os.path.abspath(os.getenv("DATABASE_URL", "app/database/bot_database.db").replace("sqlite:///", ""))
        
        # Create backup
        backup_info = create_backup(db_path)
        
        # Add backup to database
        backup = Backup(
            filename=backup_info['filename'],
            size=backup_info['size'],
            is_auto=False
        )
        db.add(backup)
        db.commit()
        
        # Send success message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
        
        await callback.message.edit_text(
            f"✅ Backup created successfully!\n\nFilename: {backup_info['filename']}\nSize: {get_file_size_str(backup_info['size'])}",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        # Send error message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
        
        await callback.message.edit_text(
            f"❌ Error creating backup: {e}",
            reply_markup=builder.as_markup()
        )
    
    # Answer callback
    await callback.answer()

async def handle_backup_selection(callback: CallbackQuery, state: FSMContext):
    """Handle backup selection."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get backup ID
    backup_id = int(callback.data.split("_")[1])
    
    # Get backup
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    
    if not backup:
        await callback.answer(get_string("error_occurred", lang))
        return
    
    # Create backup options keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Restore Backup", callback_data=f"restore_backup_{backup.id}")
    builder.button(text="❌ Delete Backup", callback_data=f"delete_backup_{backup.id}")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
    builder.adjust(1)
    
    # Send backup options message
    backup_date = backup.created_at.strftime("%Y-%m-%d %H:%M:%S")
    backup_size = get_file_size_str(backup.size)
    backup_type = "Automatic" if backup.is_auto else "Manual"
    
    await callback.message.edit_text(
        f"💾 <b>Backup Details</b>\n\nFilename: {backup.filename}\nDate: {backup_date}\nSize: {backup_size}\nType: {backup_type}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_restore_backup(callback: CallbackQuery, state: FSMContext):
    """Handle restore backup."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get backup ID
    backup_id = int(callback.data.split("_")[2])
    
    # Get backup
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    
    if not backup:
        await callback.answer(get_string("error_occurred", lang))
        return
    
    # Send restoring backup message
    await callback.message.edit_text("⏳ Restoring backup...")
    
    try:
        # Get database path
        db_path = os.path.abspath(os.getenv("DATABASE_URL", "app/database/bot_database.db").replace("sqlite:///", ""))
        
        # Restore backup
        restore_backup(backup.filename, db_path)
        
        # Send success message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
        
        await callback.message.edit_text(
            "✅ Backup restored successfully!",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        # Send error message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
        
        await callback.message.edit_text(
            f"❌ Error restoring backup: {e}",
            reply_markup=builder.as_markup()
        )
    
    # Answer callback
    await callback.answer()

async def handle_delete_backup(callback: CallbackQuery, state: FSMContext):
    """Handle delete backup."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get backup ID
    backup_id = int(callback.data.split("_")[2])
    
    # Get backup
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    
    if not backup:
        await callback.answer(get_string("error_occurred", lang))
        return
    
    # Send deleting backup message
    await callback.message.edit_text("⏳ Deleting backup...")
    
    try:
        # Delete backup file
        if os.path.exists(backup.filename):
            os.remove(backup.filename)
        
        # Delete backup from database
        db.delete(backup)
        db.commit()
        
        # Send success message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
        
        await callback.message.edit_text(
            "✅ Backup deleted successfully!",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        # Send error message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_backup")
        
        await callback.message.edit_text(
            f"❌ Error deleting backup: {e}",
            reply_markup=builder.as_markup()
        )
    
    # Answer callback
    await callback.answer()

async def handle_broadcast_all(callback: CallbackQuery, state: FSMContext):
    """Handle broadcast to all users."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to entering broadcast message
    await state.set_state(AdminStates.entering_broadcast_message)
    
    # Store broadcast type in state
    await state.update_data(broadcast_type="all")
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_broadcast")
    
    # Send broadcast prompt
    await callback.message.edit_text(
        "📣 <b>Broadcast to All Users</b>\n\nPlease enter the message to broadcast:",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_broadcast_active(callback: CallbackQuery, state: FSMContext):
    """Handle broadcast to active users."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to entering broadcast message
    await state.set_state(AdminStates.entering_broadcast_message)
    
    # Store broadcast type in state
    await state.update_data(broadcast_type="active")
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_broadcast")
    
    # Send broadcast prompt
    await callback.message.edit_text(
        "📣 <b>Broadcast to Active Users</b>\n\nPlease enter the message to broadcast:",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_broadcast_message(message: Message, state: FSMContext):
    """Handle broadcast message input."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Get broadcast type from state
    data = await state.get_data()
    broadcast_type = data.get('broadcast_type', 'all')
    
    # Store message in state
    await state.update_data(broadcast_message=message.text)
    
    # Set state to confirming broadcast
    await state.set_state(AdminStates.confirming_broadcast)
    
    # Get users count
    if broadcast_type == 'all':
        users_count = db.query(User).count()
    else:  # active
        users_count = len(get_active_users(db, 7))
    
    # Create confirmation keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("yes_button", lang), callback_data="confirm_broadcast")
    builder.button(text=get_string("no_button", lang), callback_data="cancel_broadcast")
    
    # Send confirmation message
    await message.answer(
        f"📣 <b>Broadcast Confirmation</b>\n\nYou are about to send the following message to {users_count} users:\n\n{message.text}\n\nAre you sure?",
        reply_markup=builder.as_markup()
    )

async def handle_confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """Handle confirm broadcast."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get broadcast data from state
    data = await state.get_data()
    broadcast_type = data.get('broadcast_type', 'all')
    broadcast_message = data.get('broadcast_message', '')
    
    # Send broadcasting message
    await callback.message.edit_text("⏳ Broadcasting message...")
    
    try:
        # Get users
        if broadcast_type == 'all':
            users = db.query(User).all()
        else:  # active
            users = get_active_users(db, 7)
        
        # Send message to users
        sent_count = 0
        for user in users:
            try:
                await callback.bot.send_message(
                    chat_id=user.telegram_id,
                    text=broadcast_message
                )
                sent_count += 1
            except Exception as e:
                # Log error
                logging.error(f"Error sending broadcast to user {user.telegram_id}: {e}")
        
        # Send success message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
        
        await callback.message.edit_text(
            f"✅ Broadcast sent successfully to {sent_count} users!",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        # Send error message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("back_button", lang), callback_data="back_to_admin")
        
        await callback.message.edit_text(
            f"❌ Error broadcasting message: {e}",
            reply_markup=builder.as_markup()
        )
    
    # Reset state
    await state.clear()
    
    # Answer callback
    await callback.answer()

def register_admin_handlers(dp):
    """Register admin handlers."""
    # Admin command
    dp.message.register(admin_command, Command("admin"))
    
    # Admin menu handlers
    dp.callback_query.register(handle_admin_users, F.data == "admin_users")
    dp.callback_query.register(handle_admin_categories, F.data == "admin_categories")
    dp.callback_query.register(handle_admin_formats, F.data == "admin_formats")
    dp.callback_query.register(handle_admin_subscriptions, F.data == "admin_subscriptions")
    dp.callback_query.register(handle_admin_settings, F.data == "admin_settings")
    dp.callback_query.register(handle_admin_statistics, F.data == "admin_statistics")
    dp.callback_query.register(handle_admin_backup, F.data == "admin_backup")
    dp.callback_query.register(handle_admin_broadcast, F.data == "admin_broadcast")
    
    # Backup handlers
    dp.callback_query.register(handle_create_backup, F.data == "create_backup")
    dp.callback_query.register(handle_backup_selection, F.data.startswith("backup_"))
    dp.callback_query.register(handle_restore_backup, F.data.startswith("restore_backup_"))
    dp.callback_query.register(handle_delete_backup, F.data.startswith("delete_backup_"))
    
    # Broadcast handlers
    dp.callback_query.register(handle_broadcast_all, F.data == "broadcast_all")
    dp.callback_query.register(handle_broadcast_active, F.data == "broadcast_active")
    dp.message.register(handle_broadcast_message, AdminStates.entering_broadcast_message)
    dp.callback_query.register(handle_confirm_broadcast, F.data == "confirm_broadcast")
    
    # Add router to dispatcher
    dp.include_router(router)