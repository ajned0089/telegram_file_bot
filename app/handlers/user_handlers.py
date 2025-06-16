from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..database.db import get_db
from ..database.models import User
from ..utils.helpers import get_or_create_user, get_user_language, check_subscription, get_subscription_buttons
from ..localization.strings import get_string

router = Router()

async def start_command(message: Message, state: FSMContext):
    """Handle /start command."""
    # Get database session
    db = next(get_db())
    
    # Get or create user
    user = get_or_create_user(
        db=db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code or "en"
    )
    
    # Get user language
    lang = user.language_code
    
    # Check if user is subscribed to required channels
    if not await check_subscription(message.from_user.id, message.bot, db):
        # User is not subscribed to required channels
        await message.answer(
            get_string("subscription_required", lang),
            reply_markup=get_subscription_buttons(db, lang)
        )
        return
    
    # Check if start command contains a parameter (for file sharing)
    if message.text and len(message.text.split()) > 1:
        param = message.text.split()[1]
        
        # Handle file sharing
        if param.startswith("file_"):
            file_code = param.replace("file_", "")
            # Redirect to file download handler
            from .file_handlers import download_file
            await download_file(message, file_code)
            return
        
        # Handle referral
        if param.startswith("ref_"):
            referral_code = param
            # Check if referral code is valid
            referrer = db.query(User).filter(User.referral_code == referral_code).first()
            
            if referrer and referrer.telegram_id != message.from_user.id:
                # Update user's referrer
                user.referred_by = referrer.id
                db.commit()
    
    # Create main menu keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("upload_button", lang), callback_data="upload")
    builder.button(text=get_string("my_files_button", lang), callback_data="my_files")
    builder.button(text=get_string("search_button", lang), callback_data="search")
    builder.button(text=get_string("settings_button", lang), callback_data="settings")
    builder.button(text=get_string("language_button", lang), callback_data="language")
    builder.button(text=get_string("help_button", lang), callback_data="help")
    
    # Add admin button if user is admin
    if user.is_admin:
        builder.button(text=get_string("admin_button", lang), callback_data="admin")
    
    builder.adjust(2)
    
    # Send welcome message
    await message.answer(
        get_string("welcome", lang),
        reply_markup=builder.as_markup()
    )
    
    # Reset state
    await state.clear()

async def help_command(message: Message):
    """Handle /help command."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Create help keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("upload_button", lang), callback_data="upload")
    builder.button(text=get_string("my_files_button", lang), callback_data="my_files")
    builder.button(text=get_string("search_button", lang), callback_data="search")
    builder.button(text=get_string("settings_button", lang), callback_data="settings")
    builder.adjust(2)
    
    # Send help message
    help_text = f"""
<b>📚 Bot Help</b>

This bot allows you to upload and share files with others using unique links.

<b>Commands:</b>
/start - Start the bot
/help - Show this help message
/upload - Upload a file
/myfiles - View your files
/search - Search for files
/settings - Change settings
/language - Change language
/myref - Your referral link
/cancel - Cancel current operation

<b>How to use:</b>
1. Upload a file using /upload command or the Upload button
2. Fill in the required information about the file
3. Share the generated link with others
4. Others can download the file by clicking the link

<b>Need more help?</b>
Contact the bot administrator for assistance.
"""
    
    await message.answer(
        help_text,
        reply_markup=builder.as_markup()
    )

async def settings_command(message: Message):
    """Handle /settings command."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Create settings keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("language_button", lang), callback_data="language")
    builder.button(text=get_string("referral_button", lang), callback_data="my_referral")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(2)
    
    # Send settings message
    await message.answer(
        f"⚙️ <b>{get_string('settings', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )

async def language_command(message: Message):
    """Handle /language command."""
    # Create language keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English", callback_data="set_lang_en")
    builder.button(text="🇸🇦 العربية", callback_data="set_lang_ar")
    builder.button(text="« Back", callback_data="back_to_settings")
    builder.adjust(2)
    
    # Send language message
    await message.answer(
        "🌐 <b>Select Language / اختر اللغة</b>",
        reply_markup=builder.as_markup()
    )

async def my_referral_command(message: Message):
    """Handle /myref command."""
    # Get database session
    db = next(get_db())
    
    # Get user
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        return
    
    # Get user language
    lang = user.language_code
    
    # Count referred users
    referred_count = db.query(User).filter(User.referred_by == user.id).count()
    
    # Generate referral link
    bot_username = (await message.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("back_button", lang), callback_data="back_to_settings")
    
    # Send referral message
    await message.answer(
        get_string("my_referral", lang).format(link=referral_link, count=referred_count),
        reply_markup=builder.as_markup()
    )

async def my_files_command(message: Message):
    """Handle /myfiles command."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Get user files
    from ..utils.helpers import get_user_files
    files = get_user_files(db, message.from_user.id)
    
    if not files:
        # No files
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("upload_button", lang), callback_data="upload")
        builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
        
        await message.answer(
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
    await message.answer(
        get_string("my_files", lang),
        reply_markup=builder.as_markup()
    )

async def upload_command(message: Message, state: FSMContext):
    """Handle /upload command."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Check if user can upload
    from ..utils.helpers import can_upload
    if not can_upload(message.from_user.id, db):
        await message.answer(get_string("not_authorized", lang))
        return
    
    # Set state to waiting for file
    from ..utils.states import FileUploadStates
    await state.set_state(FileUploadStates.waiting_for_file)
    
    # Create cancel keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send upload message
    await message.answer(
        get_string("send_file", lang),
        reply_markup=builder.as_markup()
    )

async def search_command(message: Message, state: FSMContext):
    """Handle /search command."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Create search keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("search_by_name", lang), callback_data="search_by_name")
    builder.button(text=get_string("search_by_tag", lang), callback_data="search_by_tag")
    builder.button(text=get_string("search_by_category", lang), callback_data="search_by_category")
    builder.button(text=get_string("search_by_format", lang), callback_data="search_by_format")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(2)
    
    # Send search message
    await message.answer(
        f"🔍 <b>{get_string('search_button', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )

async def cancel_command(message: Message, state: FSMContext):
    """Handle /cancel command."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Reset state
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer(get_string("operation_cancelled", lang))
    else:
        await message.answer(get_string("no_active_operation", lang))

def register_user_handlers(dp):
    """Register user handlers."""
    # Command handlers
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(settings_command, Command("settings"))
    dp.message.register(language_command, Command("language"))
    dp.message.register(my_referral_command, Command("myref"))
    dp.message.register(my_files_command, Command("myfiles"))
    dp.message.register(upload_command, Command("upload"))
    dp.message.register(search_command, Command("search"))
    dp.message.register(cancel_command, Command("cancel"))
    
    # Add router to dispatcher
    dp.include_router(router)