from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from dotenv import load_dotenv

from ..database.db import get_db, hash_password, verify_password, generate_share_code
from ..database.models import File, Category, Format, Tag
from ..utils.states import FileUploadStates, FileDownloadStates
from ..utils.helpers import (
    get_user_language, get_file_size_str, generate_share_link,
    parse_tags, get_or_create_tags, get_file_by_share_code,
    update_file_stats, add_file_download
)
from ..localization.strings import get_string

# Load environment variables
load_dotenv()

# Get storage channel ID
STORAGE_CHANNEL_ID = os.getenv("STORAGE_CHANNEL_ID")

router = Router()

async def handle_file_upload(message: Message, state: FSMContext):
    """Handle file upload."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Check if message contains a file
    if not (message.document or message.photo or message.video or message.audio or message.voice or message.video_note):
        await message.answer(get_string("invalid_file", lang))
        return
    
    # Get file info
    if message.document:
        file_id = message.document.file_id
        file_unique_id = message.document.file_unique_id
        file_name = message.document.file_name or "document"
        file_size = message.document.file_size
        file_type = "document"
    elif message.photo:
        photo = message.photo[-1]  # Get the largest photo
        file_id = photo.file_id
        file_unique_id = photo.file_unique_id
        file_name = "photo.jpg"
        file_size = photo.file_size
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_unique_id = message.video.file_unique_id
        file_name = message.video.file_name or "video.mp4"
        file_size = message.video.file_size
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_unique_id = message.audio.file_unique_id
        file_name = message.audio.file_name or "audio"
        file_size = message.audio.file_size
        file_type = "audio"
    elif message.voice:
        file_id = message.voice.file_id
        file_unique_id = message.voice.file_unique_id
        file_name = "voice.ogg"
        file_size = message.voice.file_size
        file_type = "voice"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_unique_id = message.video_note.file_unique_id
        file_name = "video_note.mp4"
        file_size = message.video_note.file_size
        file_type = "video_note"
    
    # Check file size
    max_file_size = int(db.query(db.query("Settings").filter_by(key="max_file_size").first().value or "50"))
    if file_size > max_file_size * 1024 * 1024:
        await message.answer(get_string("file_too_large", lang).format(max_size=max_file_size))
        return
    
    # Store file info in state
    await state.update_data(
        file_id=file_id,
        file_unique_id=file_unique_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type
    )
    
    # Send file received message
    await message.answer(
        get_string("file_received", lang).format(
            file_name=file_name,
            file_size=get_file_size_str(file_size),
            file_type=file_type
        )
    )
    
    # Forward to category selection
    await select_category(message, state)

async def select_category(message: Message, state: FSMContext):
    """Select category for file."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Set state to selecting category
    await state.set_state(FileUploadStates.selecting_category)
    
    # Get main categories
    categories = db.query(Category).filter(Category.parent_id == None, Category.is_active == True).all()
    
    # Create category keyboard
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        category_name = category.name_en if lang == "en" else category.name_ar
        builder.button(text=category_name, callback_data=f"category_{category.id}")
    
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    builder.adjust(2)
    
    # Send category selection message
    await message.answer(
        get_string("select_category", lang),
        reply_markup=builder.as_markup()
    )

async def handle_category_selection(callback: CallbackQuery, state: FSMContext):
    """Handle category selection."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get category ID
    category_id = int(callback.data.split("_")[1])
    
    # Store category ID in state
    await state.update_data(category_id=category_id)
    
    # Check if category has subcategories
    subcategories = db.query(Category).filter(Category.parent_id == category_id, Category.is_active == True).all()
    
    if subcategories:
        # Set state to selecting subcategory
        await state.set_state(FileUploadStates.selecting_subcategory)
        
        # Create subcategory keyboard
        builder = InlineKeyboardBuilder()
        
        for subcategory in subcategories:
            subcategory_name = subcategory.name_en if lang == "en" else subcategory.name_ar
            builder.button(text=subcategory_name, callback_data=f"subcategory_{subcategory.id}")
        
        builder.button(text=get_string("back_button", lang), callback_data="back_to_categories")
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
        builder.adjust(2)
        
        # Send subcategory selection message
        await callback.message.edit_text(
            get_string("select_subcategory", lang),
            reply_markup=builder.as_markup()
        )
    else:
        # No subcategories, proceed to format selection
        await select_format(callback.message, state, category_id)
    
    # Answer callback
    await callback.answer()

async def handle_subcategory_selection(callback: CallbackQuery, state: FSMContext):
    """Handle subcategory selection."""
    # Get subcategory ID
    subcategory_id = int(callback.data.split("_")[1])
    
    # Store subcategory ID in state
    await state.update_data(category_id=subcategory_id)
    
    # Proceed to format selection
    await select_format(callback.message, state, subcategory_id)
    
    # Answer callback
    await callback.answer()

async def select_format(message: Message, state: FSMContext, category_id):
    """Select format for file."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Set state to selecting format
    await state.set_state(FileUploadStates.selecting_format)
    
    # Get formats for category
    formats = db.query(Format).filter(Format.category_id == category_id, Format.is_active == True).all()
    
    # Create format keyboard
    builder = InlineKeyboardBuilder()
    
    for format in formats:
        format_name = format.name
        format_description = format.description_en if lang == "en" else format.description_ar
        display_text = f"{format_name} - {format_description}" if format_description else format_name
        builder.button(text=display_text, callback_data=f"format_{format.id}")
    
    builder.button(text=get_string("back_button", lang), callback_data="back_to_categories")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    builder.adjust(2)
    
    # Send format selection message
    await message.edit_text(
        get_string("select_format", lang),
        reply_markup=builder.as_markup()
    )

async def handle_format_selection(callback: CallbackQuery, state: FSMContext):
    """Handle format selection."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get format ID
    format_id = int(callback.data.split("_")[1])
    
    # Store format ID in state
    await state.update_data(format_id=format_id)
    
    # Set state to entering source
    await state.set_state(FileUploadStates.entering_source)
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("skip_button", lang), callback_data="skip_source")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send source prompt
    await callback.message.edit_text(
        get_string("enter_source", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_source_input(message: Message, state: FSMContext):
    """Handle source URL input."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Store source URL in state
    await state.update_data(source_url=message.text)
    
    # Proceed to filename input
    await state.set_state(FileUploadStates.entering_filename)
    
    # Get file data
    data = await state.get_data()
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("skip_button", lang), callback_data=f"skip_filename_{data['file_name']}")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send filename prompt
    await message.answer(
        get_string("enter_filename", lang),
        reply_markup=builder.as_markup()
    )

async def handle_skip_source(callback: CallbackQuery, state: FSMContext):
    """Handle skip source."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Store empty source URL in state
    await state.update_data(source_url=None)
    
    # Proceed to filename input
    await state.set_state(FileUploadStates.entering_filename)
    
    # Get file data
    data = await state.get_data()
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("skip_button", lang), callback_data=f"skip_filename_{data['file_name']}")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send filename prompt
    await callback.message.edit_text(
        get_string("enter_filename", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_filename_input(message: Message, state: FSMContext):
    """Handle filename input."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Store filename in state
    await state.update_data(file_name=message.text)
    
    # Proceed to tags input
    await state.set_state(FileUploadStates.entering_tags)
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("skip_button", lang), callback_data="skip_tags")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send tags prompt
    await message.answer(
        get_string("enter_tags", lang),
        reply_markup=builder.as_markup()
    )

async def handle_skip_filename(callback: CallbackQuery, state: FSMContext):
    """Handle skip filename."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Keep original filename (already in state)
    
    # Proceed to tags input
    await state.set_state(FileUploadStates.entering_tags)
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("skip_button", lang), callback_data="skip_tags")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send tags prompt
    await callback.message.edit_text(
        get_string("enter_tags", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_tags_input(message: Message, state: FSMContext):
    """Handle tags input."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Parse tags
    tags = parse_tags(message.text)
    
    # Store tags in state
    await state.update_data(tags=tags)
    
    # Check if password protection is enabled
    password_protection = db.query(db.query("Settings").filter_by(key="password_protection").first().value or "true")
    
    if password_protection.lower() == "true":
        # Proceed to password prompt
        await state.set_state(FileUploadStates.asking_password)
        
        # Create keyboard
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("yes_button", lang), callback_data="set_password_yes")
        builder.button(text=get_string("no_button", lang), callback_data="set_password_no")
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
        
        # Send password prompt
        await message.answer(
            get_string("set_password", lang),
            reply_markup=builder.as_markup()
        )
    else:
        # Skip password, proceed to file upload
        await state.update_data(password=None)
        await upload_file_to_channel(message, state)

async def handle_skip_tags(callback: CallbackQuery, state: FSMContext):
    """Handle skip tags."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Store empty tags in state
    await state.update_data(tags=[])
    
    # Check if password protection is enabled
    password_protection = db.query(db.query("Settings").filter_by(key="password_protection").first().value or "true")
    
    if password_protection.lower() == "true":
        # Proceed to password prompt
        await state.set_state(FileUploadStates.asking_password)
        
        # Create keyboard
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("yes_button", lang), callback_data="set_password_yes")
        builder.button(text=get_string("no_button", lang), callback_data="set_password_no")
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
        
        # Send password prompt
        await callback.message.edit_text(
            get_string("set_password", lang),
            reply_markup=builder.as_markup()
        )
    else:
        # Skip password, proceed to file upload
        await state.update_data(password=None)
        await upload_file_to_channel(callback.message, state)
    
    # Answer callback
    await callback.answer()

async def handle_set_password_yes(callback: CallbackQuery, state: FSMContext):
    """Handle set password yes."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to entering password
    await state.set_state(FileUploadStates.entering_password)
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_upload")
    
    # Send password prompt
    await callback.message.edit_text(
        get_string("enter_password", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_set_password_no(callback: CallbackQuery, state: FSMContext):
    """Handle set password no."""
    # Store empty password in state
    await state.update_data(password=None)
    
    # Proceed to file upload
    await upload_file_to_channel(callback.message, state)
    
    # Answer callback
    await callback.answer()

async def handle_password_input(message: Message, state: FSMContext):
    """Handle password input."""
    # Get database session
    db = next(get_db())
    
    # Hash password
    hashed_password = hash_password(message.text)
    
    # Store password in state
    await state.update_data(password=hashed_password)
    
    # Proceed to file upload
    await upload_file_to_channel(message, state)

async def upload_file_to_channel(message: Message, state: FSMContext):
    """Upload file to storage channel."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Get file data
    data = await state.get_data()
    
    # Send processing message
    processing_message = await message.answer(get_string("processing_file", lang))
    
    try:
        # Forward file to storage channel
        if data['file_type'] == 'document':
            sent_message = await message.bot.send_document(
                chat_id=STORAGE_CHANNEL_ID,
                document=data['file_id'],
                caption=data['file_name']
            )
        elif data['file_type'] == 'photo':
            sent_message = await message.bot.send_photo(
                chat_id=STORAGE_CHANNEL_ID,
                photo=data['file_id'],
                caption=data['file_name']
            )
        elif data['file_type'] == 'video':
            sent_message = await message.bot.send_video(
                chat_id=STORAGE_CHANNEL_ID,
                video=data['file_id'],
                caption=data['file_name']
            )
        elif data['file_type'] == 'audio':
            sent_message = await message.bot.send_audio(
                chat_id=STORAGE_CHANNEL_ID,
                audio=data['file_id'],
                caption=data['file_name']
            )
        elif data['file_type'] == 'voice':
            sent_message = await message.bot.send_voice(
                chat_id=STORAGE_CHANNEL_ID,
                voice=data['file_id'],
                caption=data['file_name']
            )
        elif data['file_type'] == 'video_note':
            sent_message = await message.bot.send_video_note(
                chat_id=STORAGE_CHANNEL_ID,
                video_note=data['file_id']
            )
        
        # Generate share code
        share_code = generate_share_code()
        
        # Generate share link
        bot_username = (await message.bot.get_me()).username
        share_link = generate_share_link(bot_username, share_code)
        
        # Get user
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        # Create file record
        new_file = File(
            telegram_file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            file_name=data['file_name'],
            file_size=data['file_size'],
            file_type=data['file_type'],
            message_id=sent_message.message_id,
            category_id=data['category_id'],
            format_id=data.get('format_id'),
            owner_id=user.id,
            source_url=data.get('source_url'),
            share_link=share_link,
            share_code=share_code,
            password=data.get('password')
        )
        
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        # Add tags
        if data.get('tags'):
            tag_objects = get_or_create_tags(db, data['tags'])
            new_file.tags = tag_objects
            db.commit()
        
        # Delete processing message
        await processing_message.delete()
        
        # Send success message
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("upload_button", lang), callback_data="upload")
        builder.button(text=get_string("my_files_button", lang), callback_data="my_files")
        builder.adjust(2)
        
        await message.answer(
            f"{get_string('file_uploaded', lang)}\n\n{get_string('share_link_created', lang).format(link=share_link)}",
            reply_markup=builder.as_markup()
        )
        
        # Reset state
        await state.clear()
        
    except Exception as e:
        # Log error
        logging.error(f"Error uploading file: {e}")
        
        # Delete processing message
        await processing_message.delete()
        
        # Send error message
        await message.answer(get_string("error_occurred", lang))
        
        # Reset state
        await state.clear()

async def download_file(message: Message, file_code: str):
    """Download file using share code."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Get file by share code
    file = get_file_by_share_code(db, file_code)
    
    if not file:
        await message.answer(get_string("file_not_found", lang))
        return
    
    # Check if file is password protected
    if file.password:
        # Set state to entering password
        from ..utils.states import FileDownloadStates
        state = FSMContext(message.bot.storage, message.from_user.id, message.chat.id)
        await state.set_state(FileDownloadStates.entering_password)
        
        # Store file ID in state
        await state.update_data(file_id=file.id)
        
        # Create keyboard
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_download")
        
        # Send password prompt
        await message.answer(
            get_string("enter_password_to_download", lang),
            reply_markup=builder.as_markup()
        )
        return
    
    # No password, proceed to download
    await send_file(message, file)

async def handle_download_password(message: Message, state: FSMContext):
    """Handle download password input."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Get file ID from state
    data = await state.get_data()
    file_id = data['file_id']
    
    # Get file
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        await message.answer(get_string("file_not_found", lang))
        await state.clear()
        return
    
    # Verify password
    if not verify_password(message.text, file.password):
        # Wrong password
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("try_again", lang), callback_data="try_again_password")
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_download")
        
        await message.answer(
            get_string("incorrect_password", lang),
            reply_markup=builder.as_markup()
        )
        return
    
    # Password correct, proceed to download
    await state.clear()
    await send_file(message, file)

async def send_file(message: Message, file):
    """Send file to user."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Send downloading message
    downloading_message = await message.answer(get_string("downloading_file", lang))
    
    try:
        # Forward file from storage channel
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=STORAGE_CHANNEL_ID,
            message_id=file.message_id
        )
        
        # Update file stats
        update_file_stats(db, file.id, is_download=True)
        
        # Add download record
        add_file_download(db, file.id, message.from_user.id)
        
        # Delete downloading message
        await downloading_message.delete()
        
        # Send success message
        await message.answer(get_string("file_sent", lang))
        
    except Exception as e:
        # Log error
        logging.error(f"Error sending file: {e}")
        
        # Delete downloading message
        await downloading_message.delete()
        
        # Send error message
        await message.answer(get_string("error_occurred", lang))

def register_file_handlers(dp):
    """Register file handlers."""
    # File upload handlers
    dp.message.register(handle_file_upload, F.document | F.photo | F.video | F.audio | F.voice | F.video_note, FileUploadStates.waiting_for_file)
    dp.callback_query.register(handle_category_selection, F.data.startswith("category_"))
    dp.callback_query.register(handle_subcategory_selection, F.data.startswith("subcategory_"))
    dp.callback_query.register(handle_format_selection, F.data.startswith("format_"))
    dp.message.register(handle_source_input, FileUploadStates.entering_source)
    dp.callback_query.register(handle_skip_source, F.data == "skip_source")
    dp.message.register(handle_filename_input, FileUploadStates.entering_filename)
    dp.callback_query.register(handle_skip_filename, F.data.startswith("skip_filename_"))
    dp.message.register(handle_tags_input, FileUploadStates.entering_tags)
    dp.callback_query.register(handle_skip_tags, F.data == "skip_tags")
    dp.callback_query.register(handle_set_password_yes, F.data == "set_password_yes")
    dp.callback_query.register(handle_set_password_no, F.data == "set_password_no")
    dp.message.register(handle_password_input, FileUploadStates.entering_password)
    
    # File download handlers
    dp.message.register(handle_download_password, FileDownloadStates.entering_password)
    
    # Add router to dispatcher
    dp.include_router(router)