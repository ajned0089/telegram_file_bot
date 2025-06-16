import os
import sys
from dotenv import load_dotenv
from app.database.db import init_db, add_admin_user
from app.database.models import Category, Format, Settings, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
Session = sessionmaker(bind=engine)
session = Session()

def init_categories():
    """Initialize categories."""
    # Check if categories exist
    if session.query(Category).count() > 0:
        print("Categories already exist, skipping...")
        return
    
    # Create main categories
    documents = Category(name_en="Documents", name_ar="مستندات", is_active=True)
    media = Category(name_en="Media", name_ar="وسائط", is_active=True)
    software = Category(name_en="Software", name_ar="برامج", is_active=True)
    other = Category(name_en="Other", name_ar="أخرى", is_active=True)
    
    session.add_all([documents, media, software, other])
    session.commit()
    
    # Create subcategories
    # Documents subcategories
    docs_office = Category(name_en="Office Documents", name_ar="مستندات أوفيس", parent_id=documents.id, is_active=True)
    docs_pdf = Category(name_en="PDF Files", name_ar="ملفات PDF", parent_id=documents.id, is_active=True)
    docs_ebooks = Category(name_en="E-Books", name_ar="كتب إلكترونية", parent_id=documents.id, is_active=True)
    
    # Media subcategories
    media_images = Category(name_en="Images", name_ar="صور", parent_id=media.id, is_active=True)
    media_videos = Category(name_en="Videos", name_ar="فيديوهات", parent_id=media.id, is_active=True)
    media_audio = Category(name_en="Audio", name_ar="صوتيات", parent_id=media.id, is_active=True)
    
    # Software subcategories
    software_windows = Category(name_en="Windows", name_ar="ويندوز", parent_id=software.id, is_active=True)
    software_mac = Category(name_en="macOS", name_ar="ماك", parent_id=software.id, is_active=True)
    software_mobile = Category(name_en="Mobile Apps", name_ar="تطبيقات الجوال", parent_id=software.id, is_active=True)
    
    session.add_all([
        docs_office, docs_pdf, docs_ebooks,
        media_images, media_videos, media_audio,
        software_windows, software_mac, software_mobile
    ])
    session.commit()
    
    print("Categories initialized successfully!")

def init_formats():
    """Initialize formats."""
    # Check if formats exist
    if session.query(Format).count() > 0:
        print("Formats already exist, skipping...")
        return
    
    # Get categories
    docs_office = session.query(Category).filter_by(name_en="Office Documents").first()
    docs_pdf = session.query(Category).filter_by(name_en="PDF Files").first()
    docs_ebooks = session.query(Category).filter_by(name_en="E-Books").first()
    media_images = session.query(Category).filter_by(name_en="Images").first()
    media_videos = session.query(Category).filter_by(name_en="Videos").first()
    media_audio = session.query(Category).filter_by(name_en="Audio").first()
    software_windows = session.query(Category).filter_by(name_en="Windows").first()
    software_mac = session.query(Category).filter_by(name_en="macOS").first()
    software_mobile = session.query(Category).filter_by(name_en="Mobile Apps").first()
    
    # Create formats
    # Office formats
    docx = Format(name="DOCX", description_en="Microsoft Word Document", description_ar="مستند مايكروسوفت وورد", category_id=docs_office.id, is_active=True)
    xlsx = Format(name="XLSX", description_en="Microsoft Excel Spreadsheet", description_ar="جدول بيانات مايكروسوفت إكسل", category_id=docs_office.id, is_active=True)
    pptx = Format(name="PPTX", description_en="Microsoft PowerPoint Presentation", description_ar="عرض تقديمي مايكروسوفت باوربوينت", category_id=docs_office.id, is_active=True)
    
    # PDF formats
    pdf = Format(name="PDF", description_en="Portable Document Format", description_ar="تنسيق المستندات المحمولة", category_id=docs_pdf.id, is_active=True)
    
    # E-Book formats
    epub = Format(name="EPUB", description_en="Electronic Publication", description_ar="نشر إلكتروني", category_id=docs_ebooks.id, is_active=True)
    mobi = Format(name="MOBI", description_en="Mobipocket E-Book", description_ar="كتاب إلكتروني موبي", category_id=docs_ebooks.id, is_active=True)
    
    # Image formats
    jpg = Format(name="JPG", description_en="JPEG Image", description_ar="صورة JPEG", category_id=media_images.id, is_active=True)
    png = Format(name="PNG", description_en="Portable Network Graphics", description_ar="رسومات الشبكة المحمولة", category_id=media_images.id, is_active=True)
    gif = Format(name="GIF", description_en="Graphics Interchange Format", description_ar="تنسيق تبادل الرسومات", category_id=media_images.id, is_active=True)
    
    # Video formats
    mp4 = Format(name="MP4", description_en="MPEG-4 Video", description_ar="فيديو MPEG-4", category_id=media_videos.id, is_active=True)
    avi = Format(name="AVI", description_en="Audio Video Interleave", description_ar="تداخل الصوت والفيديو", category_id=media_videos.id, is_active=True)
    mkv = Format(name="MKV", description_en="Matroska Video", description_ar="فيديو ماتروسكا", category_id=media_videos.id, is_active=True)
    
    # Audio formats
    mp3 = Format(name="MP3", description_en="MPEG Audio Layer III", description_ar="طبقة الصوت MPEG III", category_id=media_audio.id, is_active=True)
    wav = Format(name="WAV", description_en="Waveform Audio", description_ar="صوت الموجة", category_id=media_audio.id, is_active=True)
    flac = Format(name="FLAC", description_en="Free Lossless Audio Codec", description_ar="ترميز الصوت غير المفقود المجاني", category_id=media_audio.id, is_active=True)
    
    # Software formats
    exe = Format(name="EXE", description_en="Executable File", description_ar="ملف تنفيذي", category_id=software_windows.id, is_active=True)
    msi = Format(name="MSI", description_en="Microsoft Installer", description_ar="مثبت مايكروسوفت", category_id=software_windows.id, is_active=True)
    dmg = Format(name="DMG", description_en="Apple Disk Image", description_ar="صورة قرص أبل", category_id=software_mac.id, is_active=True)
    pkg = Format(name="PKG", description_en="Package File", description_ar="ملف حزمة", category_id=software_mac.id, is_active=True)
    apk = Format(name="APK", description_en="Android Package", description_ar="حزمة أندرويد", category_id=software_mobile.id, is_active=True)
    ipa = Format(name="IPA", description_en="iOS App Store Package", description_ar="حزمة متجر تطبيقات iOS", category_id=software_mobile.id, is_active=True)
    
    session.add_all([
        docx, xlsx, pptx,
        pdf,
        epub, mobi,
        jpg, png, gif,
        mp4, avi, mkv,
        mp3, wav, flac,
        exe, msi, dmg, pkg, apk, ipa
    ])
    session.commit()
    
    print("Formats initialized successfully!")

def init_settings():
    """Initialize settings."""
    # Check if settings exist
    if session.query(Settings).count() > 0:
        print("Settings already exist, skipping...")
        return
    
    # Create settings
    settings = [
        Settings(key="allow_public_upload", value="true", description="Allow non-admin users to upload files"),
        Settings(key="require_subscription", value="true", description="Require users to subscribe to channels"),
        Settings(key="password_protection", value="true", description="Enable password protection for files"),
        Settings(key="max_file_size", value="50", description="Maximum file size in MB"),
        Settings(key="backup_frequency", value="24", description="Backup frequency in hours"),
        Settings(key="default_language", value="en", description="Default language for new users"),
    ]
    
    session.add_all(settings)
    session.commit()
    
    print("Settings initialized successfully!")

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    Base.metadata.create_all(engine)
    
    # Initialize data
    init_categories()
    init_formats()
    init_settings()
    
    # Add admin user if provided
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    admin_ids = [int(admin_id.strip()) for admin_id in admin_ids if admin_id.strip()]
    
    if admin_ids:
        print(f"Adding admin users: {admin_ids}")
        for admin_id in admin_ids:
            add_admin_user(admin_id)
    
    print("Database initialization completed successfully!")