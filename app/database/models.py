"""
Database models for the bot.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Float, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for file tags
file_tags = Table(
    'file_tags',
    Base.metadata,
    Column('file_id', Integer, ForeignKey('files.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Association table for file downloads
file_downloads = Table(
    'file_downloads',
    Base.metadata,
    Column('file_id', Integer, ForeignKey('files.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('download_date', DateTime, default=datetime.utcnow)
)

class User(Base):
    """User model."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default='en')
    is_admin = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    can_upload = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    referral_code = Column(String(255), unique=True, nullable=False)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    api_key = Column(String(255), nullable=True)
    
    # Relationships
    files = relationship('File', back_populates='owner')
    referred_users = relationship('User', backref='referrer', remote_side=[id])
    downloaded_files = relationship('File', secondary=file_downloads, back_populates='downloaded_by')
    notifications = relationship('Notification', back_populates='user')

class Category(Base):
    """Category model."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategories = relationship('Category', backref='parent', remote_side=[id])
    files = relationship('File', back_populates='category')
    formats = relationship('Format', back_populates='category')

class Format(Base):
    """Format model."""
    __tablename__ = 'formats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description_en = Column(String(255), nullable=True)
    description_ar = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship('Category', back_populates='formats')
    files = relationship('File', back_populates='format')

class Tag(Base):
    """Tag model."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    files = relationship('File', secondary=file_tags, back_populates='tags')

class File(Base):
    """File model."""
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    telegram_file_id = Column(String(255), nullable=False)
    file_unique_id = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    message_id = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    format_id = Column(Integer, ForeignKey('formats.id'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source_url = Column(String(255), nullable=True)
    share_link = Column(String(255), nullable=False)
    share_code = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    is_encrypted = Column(Boolean, default=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Relationships
    category = relationship('Category', back_populates='files')
    format = relationship('Format', back_populates='files')
    owner = relationship('User', back_populates='files')
    tags = relationship('Tag', secondary=file_tags, back_populates='files')
    downloaded_by = relationship('User', secondary=file_downloads, back_populates='downloaded_files')
    comments = relationship('FileComment', back_populates='file')
    ratings = relationship('FileRating', back_populates='file')

class FileDownload(Base):
    """File download model."""
    __tablename__ = 'file_download_stats'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    download_count = Column(Integer, default=1)
    first_download = Column(DateTime, default=datetime.utcnow)
    last_download = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship('File')
    user = relationship('User')

class FileComment(Base):
    """File comment model."""
    __tablename__ = 'file_comments'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship('File', back_populates='comments')
    user = relationship('User')

class FileRating(Base):
    """File rating model."""
    __tablename__ = 'file_ratings'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship('File', back_populates='ratings')
    user = relationship('User')

class SubscriptionChannel(Base):
    """Subscription channel model."""
    __tablename__ = 'subscription_channels'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(255), nullable=False)
    channel_name = Column(String(255), nullable=False)
    channel_link = Column(String(255), nullable=False)
    is_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Settings(Base):
    """Settings model."""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Backup(Base):
    """Backup model."""
    __tablename__ = 'backups'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    is_auto = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    """Notification model."""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(50), default='general')
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='notifications')

class ApiLog(Base):
    """API log model."""
    __tablename__ = 'api_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User')