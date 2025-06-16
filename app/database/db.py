import os
import logging
import secrets
import string
import hashlib
import bcrypt
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app/database/bot_database.db")

# Create database directory if it doesn't exist
db_path = DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database."""
    from .models import User, File, Category, Format, Tag, FileDownload, SubscriptionChannel, Settings, Backup
    Base.metadata.create_all(bind=engine)
    
    # Initialize settings if they don't exist
    db = next(get_db())
    if db.query(Settings).count() == 0:
        settings = [
            Settings(key="allow_public_upload", value="true", description="Allow non-admin users to upload files"),
            Settings(key="require_subscription", value="true", description="Require users to subscribe to channels"),
            Settings(key="password_protection", value="true", description="Enable password protection for files"),
            Settings(key="max_file_size", value="50", description="Maximum file size in MB"),
            Settings(key="backup_frequency", value="24", description="Backup frequency in hours"),
            Settings(key="default_language", value="en", description="Default language for new users"),
        ]
        db.add_all(settings)
        db.commit()

def add_admin_user(telegram_id: int):
    """Add admin user."""
    db = next(get_db())
    
    # Check if user exists
    from .models import User
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if user:
        # Update user to admin
        user.is_admin = True
        db.commit()
    else:
        # Create new admin user
        referral_code = f"ref_{secrets.token_hex(8)}"
        user = User(
            telegram_id=telegram_id,
            is_admin=True,
            referral_code=referral_code
        )
        db.add(user)
        db.commit()

def hash_password(password: str) -> str:
    """Hash password."""
    # Generate salt
    salt = bcrypt.gensalt()
    
    # Hash password
    hashed = bcrypt.hashpw(password.encode(), salt)
    
    return hashed.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def generate_share_code() -> str:
    """Generate share code for file."""
    # Generate random code
    code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    
    return code

def get_setting(db: Session, key: str, default: str = None) -> str:
    """Get setting value."""
    from .models import Settings
    setting = db.query(Settings).filter(Settings.key == key).first()
    
    if not setting:
        return default
    
    return setting.value

def update_setting(db: Session, key: str, value: str) -> bool:
    """Update setting value."""
    from .models import Settings
    setting = db.query(Settings).filter(Settings.key == key).first()
    
    if not setting:
        return False
    
    setting.value = value
    db.commit()
    
    return True