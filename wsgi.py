import sys
import os

# Add the project directory to the path
path = '/home/ajned0089/telegram_file_bot'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///app/database/bot_database.db'
# Add other environment variables as needed

# Import the FastAPI app
from app.web.app import app as application
