from aiogram.fsm.state import State, StatesGroup

class FileUploadStates(StatesGroup):
    """States for file upload process."""
    waiting_for_file = State()
    selecting_category = State()
    selecting_subcategory = State()
    selecting_format = State()
    entering_source = State()
    entering_filename = State()
    entering_tags = State()
    asking_password = State()
    entering_password = State()
    
class FileDownloadStates(StatesGroup):
    """States for file download process."""
    entering_password = State()
    
class SearchStates(StatesGroup):
    """States for search process."""
    entering_query = State()
    selecting_category = State()
    selecting_subcategory = State()
    selecting_format = State()
    selecting_tag = State()
    
class AdminStates(StatesGroup):
    """States for admin panel."""
    main_menu = State()
    user_management = State()
    viewing_user = State()
    category_management = State()
    adding_category = State()
    editing_category = State()
    format_management = State()
    adding_format = State()
    editing_format = State()
    subscription_management = State()
    adding_channel = State()
    editing_channel = State()
    settings_management = State()
    editing_setting = State()
    backup_management = State()
    broadcast = State()
    entering_broadcast_message = State()
    confirming_broadcast = State()