from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..database.db import get_db
from ..database.models import User, File
from ..utils.helpers import get_user_language, check_subscription, get_subscription_buttons
from ..localization.strings import get_string

router = Router()

async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Handle back to main menu."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get user
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    # Create main menu keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("upload_button", lang), callback_data="upload")
    builder.button(text=get_string("my_files_button", lang), callback_data="my_files")
    builder.button(text=get_string("search_button", lang), callback_data="search")
    builder.button(text=get_string("settings_button", lang), callback_data="settings")
    builder.button(text=get_string("language_button", lang), callback_data="language")
    builder.button(text=get_string("help_button", lang), callback_data="help")
    
    # Add admin button if user is admin
    if user and user.is_admin:
        builder.button(text=get_string("admin_button", lang), callback_data="admin")
    
    builder.adjust(2)
    
    # Send main menu message
    await callback.message.edit_text(
        get_string("welcome", lang),
        reply_markup=builder.as_markup()
    )
    
    # Reset state
    await state.clear()
    
    # Answer callback
    await callback.answer()

async def handle_back_to_settings(callback: CallbackQuery, state: FSMContext):
    """Handle back to settings."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Create settings keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("language_button", lang), callback_data="language")
    builder.button(text=get_string("referral_button", lang), callback_data="my_referral")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(2)
    
    # Send settings message
    await callback.message.edit_text(
        f"⚙️ <b>{get_string('settings', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_back_to_admin(callback: CallbackQuery, state: FSMContext):
    """Handle back to admin panel."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
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
    await callback.message.edit_text(
        f"⚙️ <b>{get_string('admin_panel', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_back_to_backup(callback: CallbackQuery, state: FSMContext):
    """Handle back to backup management."""
    from .admin_handlers import handle_admin_backup
    await handle_admin_backup(callback, state)

async def handle_language(callback: CallbackQuery, state: FSMContext):
    """Handle language selection."""
    # Create language keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English", callback_data="set_lang_en")
    builder.button(text="🇸🇦 العربية", callback_data="set_lang_ar")
    builder.button(text="« Back", callback_data="back_to_settings")
    builder.adjust(2)
    
    # Send language message
    await callback.message.edit_text(
        "🌐 <b>Select Language / اختر اللغة</b>",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_set_language(callback: CallbackQuery, state: FSMContext):
    """Handle set language."""
    # Get database session
    db = next(get_db())
    
    # Get language code
    lang_code = callback.data.split("_")[2]
    
    # Update user language
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if user:
        user.language_code = lang_code
        db.commit()
    
    # Send language changed message
    await callback.answer(get_string("language_changed", lang_code))
    
    # Return to settings
    await handle_back_to_settings(callback, state)

async def handle_my_referral(callback: CallbackQuery, state: FSMContext):
    """Handle my referral."""
    # Get database session
    db = next(get_db())
    
    # Get user
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    if not user:
        await callback.answer()
        return
    
    # Get user language
    lang = user.language_code
    
    # Count referred users
    referred_count = db.query(User).filter(User.referred_by == user.id).count()
    
    # Generate referral link
    bot_username = (await callback.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("back_button", lang), callback_data="back_to_settings")
    
    # Send referral message
    await callback.message.edit_text(
        get_string("my_referral", lang).format(link=referral_link, count=referred_count),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_upload(callback: CallbackQuery, state: FSMContext):
    """Handle upload button."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Check if user can upload
    from ..utils.helpers import can_upload
    if not can_upload(callback.from_user.id, db):
        await callback.answer(get_string("not_authorized", lang))
        return
    
    # Set state to waiting for file
    from ..utils.states import FileUploadStates
    await state.set_state(FileUploadStates.waiting_for_file)
    
    # Create cancel keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send upload message
    await callback.message.edit_text(
        get_string("send_file", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_my_files(callback: CallbackQuery, state: FSMContext):
    """Handle my files button."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get user files
    from ..utils.helpers import get_user_files
    files = get_user_files(db, callback.from_user.id)
    
    if not files:
        # No files
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("upload_button", lang), callback_data="upload")
        builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
        
        await callback.message.edit_text(
            get_string("no_files", lang),
            reply_markup=builder.as_markup()
        )
        return
    
    # Create files keyboard
    builder = InlineKeyboardBuilder()
    
    for file in files:
        builder.button(
            text=f"{file.file_name} ({file.download_count} ⬇️)",
            callback_data=f"file_{file.id}"
        )
    
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(1)
    
    # Send files message
    await callback.message.edit_text(
        get_string("my_files", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_file_details(callback: CallbackQuery, state: FSMContext):
    """Handle file details."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get file ID
    file_id = int(callback.data.split("_")[1])
    
    # Get file
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        await callback.answer(get_string("file_not_found", lang))
        return
    
    # Get file details
    file_name = file.file_name
    file_size = get_file_size_str(file.file_size)
    file_type = file.file_type
    upload_date = file.upload_date.strftime("%Y-%m-%d %H:%M")
    download_count = file.download_count
    view_count = file.view_count
    share_link = file.share_link
    
    # Get category and format
    category_name = ""
    if file.category:
        category_name = file.category.name_en if lang == "en" else file.category.name_ar
    
    format_name = ""
    if file.format:
        format_name = file.format.name
    
    # Get tags
    tags = ", ".join([tag.name for tag in file.tags])
    
    # Create file details message
    file_details = f"""
📄 <b>{file_name}</b>

📊 <b>File Information:</b>
Type: {file_type}
Size: {file_size}
Category: {category_name}
Format: {format_name}
Tags: {tags or "None"}

📈 <b>Statistics:</b>
Downloads: {download_count}
Views: {view_count}
Uploaded: {upload_date}

🔗 <b>Share Link:</b>
{share_link}
"""
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text="📤 Send File", callback_data=f"send_file_{file.id}")
    builder.button(text="📊 Download Stats", callback_data=f"file_stats_{file.id}")
    builder.button(text=get_string("back_button", lang), callback_data="my_files")
    builder.adjust(1)
    
    # Send file details message
    await callback.message.edit_text(
        file_details,
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_search(callback: CallbackQuery, state: FSMContext):
    """Handle search button."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Create search keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("search_by_name", lang), callback_data="search_by_name")
    builder.button(text=get_string("search_by_tag", lang), callback_data="search_by_tag")
    builder.button(text=get_string("search_by_category", lang), callback_data="search_by_category")
    builder.button(text=get_string("search_by_format", lang), callback_data="search_by_format")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(2)
    
    # Send search message
    await callback.message.edit_text(
        f"🔍 <b>{get_string('search_button', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_cancel_upload(callback: CallbackQuery, state: FSMContext):
    """Handle cancel upload."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Reset state
    await state.clear()
    
    # Return to main menu
    await handle_back_to_main(callback, state)
    
    # Answer callback with cancelled message
    await callback.answer(get_string("operation_cancelled", lang))

async def handle_cancel_search(callback: CallbackQuery, state: FSMContext):
    """Handle cancel search."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Reset state
    await state.clear()
    
    # Return to search menu
    await handle_search(callback, state)
    
    # Answer callback with cancelled message
    await callback.answer(get_string("operation_cancelled", lang))

async def handle_cancel_download(callback: CallbackQuery, state: FSMContext):
    """Handle cancel download."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Reset state
    await state.clear()
    
    # Return to main menu
    await handle_back_to_main(callback, state)
    
    # Answer callback with cancelled message
    await callback.answer(get_string("operation_cancelled", lang))

async def handle_cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Handle cancel broadcast."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Reset state
    await state.clear()
    
    # Return to admin panel
    await handle_back_to_admin(callback, state)
    
    # Answer callback with cancelled message
    await callback.answer(get_string("operation_cancelled", lang))

async def handle_check_subscription(callback: CallbackQuery, state: FSMContext):
    """Handle check subscription."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Check if user is subscribed to required channels
    if not check_subscription(callback.from_user.id, callback.bot, db):
        # User is not subscribed to required channels
        await callback.answer(get_string("subscription_required", lang), show_alert=True)
        return
    
    # User is subscribed, show main menu
    await handle_back_to_main(callback, state)
    
    # Answer callback with success message
    await callback.answer(get_string("subscription_checked", lang))

def register_callback_handlers(dp):
    """Register callback handlers."""
    # Navigation handlers
    dp.callback_query.register(handle_back_to_main, F.data == "back_to_main")
    dp.callback_query.register(handle_back_to_settings, F.data == "back_to_settings")
    dp.callback_query.register(handle_back_to_admin, F.data == "back_to_admin")
    dp.callback_query.register(handle_back_to_backup, F.data == "back_to_backup")
    
    # Settings handlers
    dp.callback_query.register(handle_language, F.data == "language")
    dp.callback_query.register(handle_set_language, F.data.startswith("set_lang_"))
    dp.callback_query.register(handle_my_referral, F.data == "my_referral")
    
    # Main menu handlers
    dp.callback_query.register(handle_upload, F.data == "upload")
    dp.callback_query.register(handle_my_files, F.data == "my_files")
    dp.callback_query.register(handle_search, F.data == "search")
    
    # File handlers
    dp.callback_query.register(handle_file_details, F.data.startswith("file_"))
    
    # Cancel handlers
    dp.callback_query.register(handle_cancel_upload, F.data == "cancel_upload")
    dp.callback_query.register(handle_cancel_search, F.data == "cancel_search")
    dp.callback_query.register(handle_cancel_download, F.data == "cancel_download")
    dp.callback_query.register(handle_cancel_broadcast, F.data == "cancel_broadcast")
    
    # Subscription handlers
    dp.callback_query.register(handle_check_subscription, F.data == "check_subscription")
    
    # Add router to dispatcher
    dp.include_router(router)