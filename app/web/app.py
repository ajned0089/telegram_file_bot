from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import secrets
import uvicorn
from datetime import datetime, timedelta

from ..database.db import get_db
from ..database.models import User, File, Category, Format, Tag, SubscriptionChannel, Settings, Backup
from ..utils.helpers import get_file_size_str, create_backup, restore_backup
from ..utils.analytics import get_dashboard_stats
from ..api.api import api_app

# Load environment variables
load_dotenv()

# Get admin credentials
WEB_ADMIN_USERNAME = os.getenv("WEB_ADMIN_USERNAME", "admin")
WEB_ADMIN_PASSWORD = os.getenv("WEB_ADMIN_PASSWORD", "admin")
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))

# Create FastAPI app
app = FastAPI(title="Telegram File Bot Admin Panel")

# Set up security
security = HTTPBasic()

# Set up templates
templates = Jinja2Templates(directory="app/web/templates")

# Set up static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# Mount API
app.mount("/api", api_app)

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials."""
    correct_username = secrets.compare_digest(credentials.username, WEB_ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, WEB_ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, username: str = Depends(verify_credentials), db: Session = Depends(get_db)):
    """Admin panel home page."""
    # Get dashboard statistics
    stats = get_dashboard_stats(db)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "total_users": stats["total_users"],
            "total_files": stats["total_files"],
            "total_downloads": stats["total_downloads"],
            "active_users": stats["active_users"],
            "storage_used": get_file_size_str(stats["total_size"]),
            "recent_users": stats["recent_users"],
            "recent_files": stats["recent_files"],
            "user_growth": stats["user_growth"],
            "file_uploads": stats["file_uploads"],
            "file_downloads": stats["file_downloads"],
            "popular_categories": stats["popular_categories"],
            "popular_file_types": stats["popular_file_types"]
        }
    )

@app.get("/users", response_class=HTMLResponse)
async def users(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    search: str = None
):
    """User management page."""
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get users
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%")) |
            (User.telegram_id == search if search.isdigit() else False)
        )
    
    total_users = query.count()
    users = query.order_by(User.last_activity.desc()).offset(offset).limit(limit).all()
    
    # Calculate total pages
    total_pages = (total_users + limit - 1) // limit
    
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "page": page,
            "total_pages": total_pages,
            "search": search
        }
    )

@app.get("/users/{user_id}", response_class=HTMLResponse)
async def user_details(
    request: Request,
    user_id: int,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """User details page."""
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user files
    files = db.query(File).filter(File.owner_id == user.id).all()
    
    # Get referred users
    referred_users = db.query(User).filter(User.referred_by == user.id).all()
    
    return templates.TemplateResponse(
        "user_details.html",
        {
            "request": request,
            "user": user,
            "files": files,
            "referred_users": referred_users
        }
    )

@app.post("/users/{user_id}/update")
async def update_user(
    user_id: int,
    is_admin: bool = Form(False),
    is_moderator: bool = Form(False),
    can_upload: bool = Form(True),
    is_banned: bool = Form(False),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Update user."""
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    user.is_admin = is_admin
    user.is_moderator = is_moderator
    user.can_upload = can_upload
    user.is_banned = is_banned
    
    db.commit()
    
    return RedirectResponse(url=f"/users/{user_id}", status_code=303)

@app.get("/categories", response_class=HTMLResponse)
async def categories(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Category management page."""
    # Get main categories
    main_categories = db.query(Category).filter(Category.parent_id == None).all()
    
    return templates.TemplateResponse(
        "categories.html",
        {
            "request": request,
            "categories": main_categories
        }
    )

@app.get("/categories/{category_id}", response_class=HTMLResponse)
async def category_details(
    request: Request,
    category_id: int,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Category details page."""
    # Get category
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get subcategories
    subcategories = db.query(Category).filter(Category.parent_id == category.id).all()
    
    # Get formats
    formats = db.query(Format).filter(Format.category_id == category.id).all()
    
    # Get files
    files = db.query(File).filter(File.category_id == category.id).all()
    
    return templates.TemplateResponse(
        "category_details.html",
        {
            "request": request,
            "category": category,
            "subcategories": subcategories,
            "formats": formats,
            "files": files
        }
    )

@app.post("/categories/add")
async def add_category(
    name_en: str = Form(...),
    name_ar: str = Form(...),
    parent_id: int = Form(None),
    is_active: bool = Form(True),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Add category."""
    # Create category
    category = Category(
        name_en=name_en,
        name_ar=name_ar,
        parent_id=parent_id if parent_id else None,
        is_active=is_active
    )
    
    db.add(category)
    db.commit()
    
    return RedirectResponse(url="/categories", status_code=303)

@app.post("/categories/{category_id}/update")
async def update_category(
    category_id: int,
    name_en: str = Form(...),
    name_ar: str = Form(...),
    is_active: bool = Form(True),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Update category."""
    # Get category
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update category
    category.name_en = name_en
    category.name_ar = name_ar
    category.is_active = is_active
    
    db.commit()
    
    return RedirectResponse(url=f"/categories/{category_id}", status_code=303)

@app.get("/formats", response_class=HTMLResponse)
async def formats(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Format management page."""
    # Get formats
    formats = db.query(Format).all()
    
    # Get categories for dropdown
    categories = db.query(Category).all()
    
    return templates.TemplateResponse(
        "formats.html",
        {
            "request": request,
            "formats": formats,
            "categories": categories
        }
    )

@app.post("/formats/add")
async def add_format(
    name: str = Form(...),
    description_en: str = Form(None),
    description_ar: str = Form(None),
    category_id: int = Form(None),
    is_active: bool = Form(True),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Add format."""
    # Create format
    format = Format(
        name=name,
        description_en=description_en,
        description_ar=description_ar,
        category_id=category_id if category_id else None,
        is_active=is_active
    )
    
    db.add(format)
    db.commit()
    
    return RedirectResponse(url="/formats", status_code=303)

@app.post("/formats/{format_id}/update")
async def update_format(
    format_id: int,
    name: str = Form(...),
    description_en: str = Form(None),
    description_ar: str = Form(None),
    category_id: int = Form(None),
    is_active: bool = Form(True),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Update format."""
    # Get format
    format = db.query(Format).filter(Format.id == format_id).first()
    
    if not format:
        raise HTTPException(status_code=404, detail="Format not found")
    
    # Update format
    format.name = name
    format.description_en = description_en
    format.description_ar = description_ar
    format.category_id = category_id if category_id else None
    format.is_active = is_active
    
    db.commit()
    
    return RedirectResponse(url="/formats", status_code=303)

@app.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Subscription management page."""
    # Get subscription channels
    channels = db.query(SubscriptionChannel).all()
    
    return templates.TemplateResponse(
        "subscriptions.html",
        {
            "request": request,
            "channels": channels
        }
    )

@app.post("/subscriptions/add")
async def add_subscription(
    channel_id: str = Form(...),
    channel_name: str = Form(...),
    channel_link: str = Form(...),
    is_required: bool = Form(True),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Add subscription channel."""
    # Create subscription channel
    channel = SubscriptionChannel(
        channel_id=channel_id,
        channel_name=channel_name,
        channel_link=channel_link,
        is_required=is_required
    )
    
    db.add(channel)
    db.commit()
    
    return RedirectResponse(url="/subscriptions", status_code=303)

@app.post("/subscriptions/{channel_id}/update")
async def update_subscription(
    channel_id: int,
    channel_id_value: str = Form(...),
    channel_name: str = Form(...),
    channel_link: str = Form(...),
    is_required: bool = Form(True),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Update subscription channel."""
    # Get subscription channel
    channel = db.query(SubscriptionChannel).filter(SubscriptionChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Subscription channel not found")
    
    # Update subscription channel
    channel.channel_id = channel_id_value
    channel.channel_name = channel_name
    channel.channel_link = channel_link
    channel.is_required = is_required
    
    db.commit()
    
    return RedirectResponse(url="/subscriptions", status_code=303)

@app.get("/settings", response_class=HTMLResponse)
async def settings(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Settings page."""
    # Get settings
    settings = db.query(Settings).all()
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": settings
        }
    )

@app.post("/settings/{setting_id}/update")
async def update_setting(
    setting_id: int,
    value: str = Form(...),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Update setting."""
    # Get setting
    setting = db.query(Settings).filter(Settings.id == setting_id).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    # Update setting
    setting.value = value
    
    db.commit()
    
    return RedirectResponse(url="/settings", status_code=303)

@app.get("/backups", response_class=HTMLResponse)
async def backups(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Backup management page."""
    # Get backups
    backups = db.query(Backup).order_by(Backup.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "backups.html",
        {
            "request": request,
            "backups": backups
        }
    )

@app.post("/backups/create")
async def create_backup_endpoint(
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Create backup."""
    try:
        # Get database path
        db_path = os.path.abspath(os.getenv("DATABASE_URL", "app/database/bot_database.db").replace("sqlite:///", ""))
        
        # Create backup
        backup_info = create_backup(db_path)
        
        # Add backup to database
        backup = Backup(
            filename=backup_info['filename'],
            size=backup_info['size'],
            is_auto=False
        )
        db.add(backup)
        db.commit()
        
        return RedirectResponse(url="/backups", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating backup: {e}")

@app.post("/backups/{backup_id}/restore")
async def restore_backup_endpoint(
    backup_id: int,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Restore backup."""
    try:
        # Get backup
        backup = db.query(Backup).filter(Backup.id == backup_id).first()
        
        if not backup:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        # Get database path
        db_path = os.path.abspath(os.getenv("DATABASE_URL", "app/database/bot_database.db").replace("sqlite:///", ""))
        
        # Restore backup
        restore_backup(backup.filename, db_path)
        
        return RedirectResponse(url="/backups", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring backup: {e}")

@app.post("/backups/{backup_id}/delete")
async def delete_backup(
    backup_id: int,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Delete backup."""
    try:
        # Get backup
        backup = db.query(Backup).filter(Backup.id == backup_id).first()
        
        if not backup:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        # Delete backup file
        if os.path.exists(backup.filename):
            os.remove(backup.filename)
        
        # Delete backup from database
        db.delete(backup)
        db.commit()
        
        return RedirectResponse(url="/backups", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting backup: {e}")

@app.get("/files", response_class=HTMLResponse)
async def files(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    search: str = None
):
    """File management page."""
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get files
    query = db.query(File)
    
    if search:
        query = query.filter(File.file_name.ilike(f"%{search}%"))
    
    total_files = query.count()
    files = query.order_by(File.upload_date.desc()).offset(offset).limit(limit).all()
    
    # Calculate total pages
    total_pages = (total_files + limit - 1) // limit
    
    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "files": files,
            "page": page,
            "total_pages": total_pages,
            "search": search
        }
    )

@app.get("/files/{file_id}", response_class=HTMLResponse)
async def file_details(
    request: Request,
    file_id: int,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """File details page."""
    # Get file
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file downloads
    downloads = file.downloaded_by
    
    return templates.TemplateResponse(
        "file_details.html",
        {
            "request": request,
            "file": file,
            "downloads": downloads
        }
    )

@app.post("/files/{file_id}/update")
async def update_file(
    file_id: int,
    file_name: str = Form(...),
    password: str = Form(None),
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Update file."""
    # Get file
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Update file
    file.file_name = file_name
    
    if password:
        from ..database.db import hash_password
        file.password = hash_password(password)
    
    db.commit()
    
    return RedirectResponse(url=f"/files/{file_id}", status_code=303)

@app.get("/analytics", response_class=HTMLResponse)
async def analytics(
    request: Request,
    username: str = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Analytics page."""
    # Get dashboard statistics
    stats = get_dashboard_stats(db)
    
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "stats": stats
        }
    )

def run_web_server():
    """Run web server."""
    uvicorn.run(app, host=WEB_HOST, port=WEB_PORT)