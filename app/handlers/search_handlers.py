from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..database.db import get_db
from ..database.models import Category, Format, Tag, File
from ..utils.states import SearchStates
from ..utils.helpers import (
    get_user_language, search_files_by_name, search_files_by_tag,
    search_files_by_category, search_files_by_format
)
from ..localization.strings import get_string

router = Router()

async def search_by_name(callback: CallbackQuery, state: FSMContext):
    """Search files by name."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to entering query
    await state.set_state(SearchStates.entering_query)
    
    # Store search type in state
    await state.update_data(search_type="name")
    
    # Create keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_search")
    
    # Send search prompt
    await callback.message.edit_text(
        get_string("search_prompt", lang),
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def search_by_tag(callback: CallbackQuery, state: FSMContext):
    """Search files by tag."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to selecting tag
    await state.set_state(SearchStates.selecting_tag)
    
    # Get popular tags
    tags = db.query(Tag).join(Tag.files).group_by(Tag.id).order_by(db.func.count(File.id).desc()).limit(10).all()
    
    if not tags:
        # No tags found, switch to entering query
        await state.set_state(SearchStates.entering_query)
        await state.update_data(search_type="tag")
        
        # Create keyboard
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_search")
        
        # Send search prompt
        await callback.message.edit_text(
            get_string("search_prompt", lang),
            reply_markup=builder.as_markup()
        )
    else:
        # Create tag keyboard
        builder = InlineKeyboardBuilder()
        
        for tag in tags:
            builder.button(text=tag.name, callback_data=f"tag_{tag.id}")
        
        builder.button(text=get_string("search_prompt", lang), callback_data="enter_tag_query")
        builder.button(text=get_string("back_button", lang), callback_data="back_to_search")
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_search")
        builder.adjust(2)
        
        # Send tag selection message
        await callback.message.edit_text(
            f"🏷️ <b>{get_string('search_by_tag', lang)}</b>\n\n{get_string('select_option', lang)}",
            reply_markup=builder.as_markup()
        )
    
    # Answer callback
    await callback.answer()

async def search_by_category(callback: CallbackQuery, state: FSMContext):
    """Search files by category."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to selecting category
    await state.set_state(SearchStates.selecting_category)
    
    # Get main categories
    categories = db.query(Category).filter(Category.parent_id == None, Category.is_active == True).all()
    
    # Create category keyboard
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        category_name = category.name_en if lang == "en" else category.name_ar
        builder.button(text=category_name, callback_data=f"search_category_{category.id}")
    
    builder.button(text=get_string("back_button", lang), callback_data="back_to_search")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_search")
    builder.adjust(2)
    
    # Send category selection message
    await callback.message.edit_text(
        f"📂 <b>{get_string('search_by_category', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def search_by_format(callback: CallbackQuery, state: FSMContext):
    """Search files by format."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Set state to selecting format
    await state.set_state(SearchStates.selecting_format)
    
    # Get formats
    formats = db.query(Format).filter(Format.is_active == True).all()
    
    # Create format keyboard
    builder = InlineKeyboardBuilder()
    
    for format in formats:
        format_name = format.name
        format_description = format.description_en if lang == "en" else format.description_ar
        display_text = f"{format_name} - {format_description}" if format_description else format_name
        builder.button(text=display_text, callback_data=f"search_format_{format.id}")
    
    builder.button(text=get_string("back_button", lang), callback_data="back_to_search")
    builder.button(text=get_string("cancel_button", lang), callback_data="cancel_search")
    builder.adjust(2)
    
    # Send format selection message
    await callback.message.edit_text(
        f"📄 <b>{get_string('search_by_format', lang)}</b>\n\n{get_string('select_option', lang)}",
        reply_markup=builder.as_markup()
    )
    
    # Answer callback
    await callback.answer()

async def handle_search_query(message: Message, state: FSMContext):
    """Handle search query input."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(message.from_user.id, db)
    
    # Get search type from state
    data = await state.get_data()
    search_type = data.get('search_type', 'name')
    
    # Perform search
    if search_type == 'name':
        files = search_files_by_name(db, message.text)
    elif search_type == 'tag':
        files = search_files_by_tag(db, message.text)
    
    # Display search results
    await display_search_results(message, files, lang)
    
    # Reset state
    await state.clear()

async def handle_tag_selection(callback: CallbackQuery, state: FSMContext):
    """Handle tag selection."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get tag ID
    tag_id = int(callback.data.split("_")[1])
    
    # Get tag
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        await callback.answer(get_string("error_occurred", lang))
        return
    
    # Get files with tag
    files = tag.files
    
    # Display search results
    await display_search_results(callback.message, files, lang)
    
    # Reset state
    await state.clear()
    
    # Answer callback
    await callback.answer()

async def handle_category_selection_search(callback: CallbackQuery, state: FSMContext):
    """Handle category selection for search."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get category ID
    category_id = int(callback.data.split("_")[2])
    
    # Check if category has subcategories
    subcategories = db.query(Category).filter(Category.parent_id == category_id, Category.is_active == True).all()
    
    if subcategories:
        # Set state to selecting subcategory
        await state.set_state(SearchStates.selecting_subcategory)
        
        # Store category ID in state
        await state.update_data(parent_category_id=category_id)
        
        # Create subcategory keyboard
        builder = InlineKeyboardBuilder()
        
        for subcategory in subcategories:
            subcategory_name = subcategory.name_en if lang == "en" else subcategory.name_ar
            builder.button(text=subcategory_name, callback_data=f"search_subcategory_{subcategory.id}")
        
        builder.button(text=get_string("back_button", lang), callback_data="back_to_categories_search")
        builder.button(text=get_string("cancel_button", lang), callback_data="cancel_search")
        builder.adjust(2)
        
        # Send subcategory selection message
        await callback.message.edit_text(
            f"📂 <b>{get_string('select_subcategory', lang)}</b>",
            reply_markup=builder.as_markup()
        )
    else:
        # No subcategories, search files in this category
        files = search_files_by_category(db, category_id)
        
        # Display search results
        await display_search_results(callback.message, files, lang)
        
        # Reset state
        await state.clear()
    
    # Answer callback
    await callback.answer()

async def handle_subcategory_selection_search(callback: CallbackQuery, state: FSMContext):
    """Handle subcategory selection for search."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get subcategory ID
    subcategory_id = int(callback.data.split("_")[2])
    
    # Search files in subcategory
    files = search_files_by_category(db, subcategory_id)
    
    # Display search results
    await display_search_results(callback.message, files, lang)
    
    # Reset state
    await state.clear()
    
    # Answer callback
    await callback.answer()

async def handle_format_selection_search(callback: CallbackQuery, state: FSMContext):
    """Handle format selection for search."""
    # Get database session
    db = next(get_db())
    
    # Get user language
    lang = get_user_language(callback.from_user.id, db)
    
    # Get format ID
    format_id = int(callback.data.split("_")[2])
    
    # Search files with format
    files = search_files_by_format(db, format_id)
    
    # Display search results
    await display_search_results(callback.message, files, lang)
    
    # Reset state
    await state.clear()
    
    # Answer callback
    await callback.answer()

async def display_search_results(message, files, lang):
    """Display search results."""
    if not files:
        # No results
        builder = InlineKeyboardBuilder()
        builder.button(text=get_string("search_button", lang), callback_data="search")
        builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
        
        await message.edit_text(
            get_string("no_results", lang),
            reply_markup=builder.as_markup()
        )
        return
    
    # Create results keyboard
    builder = InlineKeyboardBuilder()
    
    for file in files:
        builder.button(
            text=f"{file.file_name} ({file.download_count} ⬇️)",
            callback_data=f"file_{file.id}"
        )
    
    builder.button(text=get_string("search_button", lang), callback_data="search")
    builder.button(text=get_string("back_button", lang), callback_data="back_to_main")
    builder.adjust(1)
    
    # Send results message
    await message.edit_text(
        get_string("search_results", lang).format(count=len(files)),
        reply_markup=builder.as_markup()
    )

def register_search_handlers(dp):
    """Register search handlers."""
    # Search type handlers
    dp.callback_query.register(search_by_name, F.data == "search_by_name")
    dp.callback_query.register(search_by_tag, F.data == "search_by_tag")
    dp.callback_query.register(search_by_category, F.data == "search_by_category")
    dp.callback_query.register(search_by_format, F.data == "search_by_format")
    
    # Search query handlers
    dp.message.register(handle_search_query, SearchStates.entering_query)
    
    # Selection handlers
    dp.callback_query.register(handle_tag_selection, F.data.startswith("tag_"))
    dp.callback_query.register(handle_category_selection_search, F.data.startswith("search_category_"))
    dp.callback_query.register(handle_subcategory_selection_search, F.data.startswith("search_subcategory_"))
    dp.callback_query.register(handle_format_selection_search, F.data.startswith("search_format_"))
    
    # Add router to dispatcher
    dp.include_router(router)