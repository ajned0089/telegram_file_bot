from .user_handlers import register_user_handlers
from .admin_handlers import register_admin_handlers
from .file_handlers import register_file_handlers
from .search_handlers import register_search_handlers
from .callback_handlers import register_callback_handlers

__all__ = [
    'register_user_handlers',
    'register_admin_handlers',
    'register_file_handlers',
    'register_search_handlers',
    'register_callback_handlers'
]