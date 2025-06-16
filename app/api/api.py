"""
API for the bot.
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header, File, UploadFile
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from ..database.db import get_db
from ..database.models import User, File as DBFile, Category, Format, Tag, ApiLog
from ..utils.security import validate_api_key, sanitize_filename
from ..utils.helpers import get_file_size_str

# Create FastAPI app
api_app = FastAPI(title="Telegram File Bot API", version="1.0.0")

# API key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# Log API request
async def log_api_request(request: Request, status_code: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Log API request."""
    api_log = ApiLog(
        user_id=user_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=status_code,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(api_log)
    db.commit()

# Verify API key
async def verify_api_key(api_key: str = Depends(API_KEY_HEADER), db: Session = Depends(get_db)):
    """Verify API key."""
    user = db.query(User).filter(User.api_key == api_key).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user

# API routes
@api_app.get("/")
async def root():
    """API root."""
    return {"message": "Welcome to Telegram File Bot API"}

@api_app.get("/users/me")
async def get_current_user(user: User = Depends(verify_api_key), db: Session = Depends(get_db)):
    """Get current user."""
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin,
        "is_moderator": user.is_moderator,
        "can_upload": user.can_upload,
        "created_at": user.created_at.isoformat(),
        "last_activity": user.last_activity.isoformat(),
        "referral_code": user.referral_code
    }

@api_app.get("/files")
async def get_files(
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    format_id: Optional[int] = None,
    search: Optional[str] = None
):
    """Get files."""
    # Build query
    query = db.query(DBFile)
    
    # Filter by owner
    if not user.is_admin and not user.is_moderator:
        query = query.filter(DBFile.owner_id == user.id)
    
    # Apply filters
    if category_id:
        query = query.filter(DBFile.category_id == category_id)
    
    if format_id:
        query = query.filter(DBFile.format_id == format_id)
    
    if search:
        query = query.filter(DBFile.file_name.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    files = query.order_by(DBFile.upload_date.desc()).offset(skip).limit(limit).all()
    
    # Format response
    result = []
    for file in files:
        result.append({
            "id": file.id,
            "file_name": file.file_name,
            "file_size": file.file_size,
            "file_size_str": get_file_size_str(file.file_size),
            "file_type": file.file_type,
            "category_id": file.category_id,
            "format_id": file.format_id,
            "share_link": file.share_link,
            "is_encrypted": file.is_encrypted,
            "upload_date": file.upload_date.isoformat(),
            "download_count": file.download_count,
            "view_count": file.view_count,
            "rating": file.rating,
            "rating_count": file.rating_count,
            "tags": [tag.name for tag in file.tags]
        })
    
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "files": result
    }

@api_app.get("/files/{file_id}")
async def get_file(
    file_id: int,
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Get file details."""
    # Get file
    file = db.query(DBFile).filter(DBFile.id == file_id).first()
    
    if not file:
        await log_api_request(Request, status.HTTP_404_NOT_FOUND, user.id, db)
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if user has access to file
    if not user.is_admin and not user.is_moderator and file.owner_id != user.id:
        await log_api_request(Request, status.HTTP_403_FORBIDDEN, user.id, db)
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Format response
    result = {
        "id": file.id,
        "file_name": file.file_name,
        "file_size": file.file_size,
        "file_size_str": get_file_size_str(file.file_size),
        "file_type": file.file_type,
        "category_id": file.category_id,
        "format_id": file.format_id,
        "owner_id": file.owner_id,
        "source_url": file.source_url,
        "share_link": file.share_link,
        "share_code": file.share_code,
        "is_encrypted": file.is_encrypted,
        "upload_date": file.upload_date.isoformat(),
        "expiry_date": file.expiry_date.isoformat() if file.expiry_date else None,
        "download_count": file.download_count,
        "view_count": file.view_count,
        "rating": file.rating,
        "rating_count": file.rating_count,
        "tags": [tag.name for tag in file.tags],
        "category": {
            "id": file.category.id,
            "name_en": file.category.name_en,
            "name_ar": file.category.name_ar
        } if file.category else None,
        "format": {
            "id": file.format.id,
            "name": file.format.name,
            "description_en": file.format.description_en,
            "description_ar": file.format.description_ar
        } if file.format else None,
        "owner": {
            "id": file.owner.id,
            "telegram_id": file.owner.telegram_id,
            "username": file.owner.username,
            "first_name": file.owner.first_name,
            "last_name": file.owner.last_name
        }
    }
    
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return result

@api_app.get("/categories")
async def get_categories(
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db),
    parent_id: Optional[int] = None
):
    """Get categories."""
    # Build query
    query = db.query(Category)
    
    # Filter by parent
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id == None)
    
    # Get categories
    categories = query.all()
    
    # Format response
    result = []
    for category in categories:
        result.append({
            "id": category.id,
            "name_en": category.name_en,
            "name_ar": category.name_ar,
            "parent_id": category.parent_id,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat(),
            "subcategories_count": len(category.subcategories),
            "files_count": len(category.files)
        })
    
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return result

@api_app.get("/formats")
async def get_formats(
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db),
    category_id: Optional[int] = None
):
    """Get formats."""
    # Build query
    query = db.query(Format)
    
    # Filter by category
    if category_id:
        query = query.filter(Format.category_id == category_id)
    
    # Get formats
    formats = query.all()
    
    # Format response
    result = []
    for format in formats:
        result.append({
            "id": format.id,
            "name": format.name,
            "description_en": format.description_en,
            "description_ar": format.description_ar,
            "category_id": format.category_id,
            "is_active": format.is_active,
            "created_at": format.created_at.isoformat(),
            "files_count": len(format.files)
        })
    
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return result

@api_app.get("/tags")
async def get_tags(
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db),
    search: Optional[str] = None
):
    """Get tags."""
    # Build query
    query = db.query(Tag)
    
    # Apply search
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))
    
    # Get tags
    tags = query.all()
    
    # Format response
    result = []
    for tag in tags:
        result.append({
            "id": tag.id,
            "name": tag.name,
            "created_at": tag.created_at.isoformat(),
            "files_count": len(tag.files)
        })
    
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return result

@api_app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category_id: Optional[int] = None,
    format_id: Optional[int] = None,
    tags: Optional[str] = None,
    source_url: Optional[str] = None,
    password: Optional[str] = None,
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Upload file."""
    # Check if user can upload
    if not user.can_upload and not user.is_admin and not user.is_moderator:
        await log_api_request(Request, status.HTTP_403_FORBIDDEN, user.id, db)
        raise HTTPException(status_code=403, detail="User cannot upload files")
    
    # Check file size
    from ..database.db import get_setting
    max_file_size = int(get_setting(db, "max_file_size", "50")) * 1024 * 1024
    
    if file.size > max_file_size:
        await log_api_request(Request, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, user.id, db)
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {max_file_size / (1024 * 1024)} MB")
    
    # Sanitize filename
    file_name = sanitize_filename(file.filename)
    
    # Save file temporarily
    temp_file_path = f"temp_{file_name}"
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # TODO: Implement file upload to Telegram
        # For now, just return success
        
        # Parse tags
        tag_list = []
        if tags:
            from ..utils.helpers import parse_tags, get_or_create_tags
            tag_names = parse_tags(tags)
            tag_list = get_or_create_tags(db, tag_names)
        
        # Generate share code and link
        from ..database.db import generate_share_code
        from ..utils.helpers import generate_share_link
        share_code = generate_share_code()
        bot_username = "your_bot_username"  # TODO: Get from settings
        share_link = generate_share_link(bot_username, share_code)
        
        # Hash password if provided
        hashed_password = None
        if password:
            from ..database.db import hash_password
            hashed_password = hash_password(password)
        
        # Create file record
        new_file = DBFile(
            telegram_file_id="temp_id",  # TODO: Get from Telegram
            file_unique_id="temp_unique_id",  # TODO: Get from Telegram
            file_name=file_name,
            file_size=os.path.getsize(temp_file_path),
            file_type=file.content_type,
            message_id=0,  # TODO: Get from Telegram
            category_id=category_id,
            format_id=format_id,
            owner_id=user.id,
            source_url=source_url,
            share_link=share_link,
            share_code=share_code,
            password=hashed_password
        )
        
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        
        # Add tags
        if tag_list:
            new_file.tags = tag_list
            db.commit()
        
        await log_api_request(Request, status.HTTP_201_CREATED, user.id, db)
        
        return {
            "id": new_file.id,
            "file_name": new_file.file_name,
            "file_size": new_file.file_size,
            "file_size_str": get_file_size_str(new_file.file_size),
            "share_link": new_file.share_link,
            "share_code": new_file.share_code
        }
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@api_app.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    user: User = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Delete file."""
    # Get file
    file = db.query(DBFile).filter(DBFile.id == file_id).first()
    
    if not file:
        await log_api_request(Request, status.HTTP_404_NOT_FOUND, user.id, db)
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if user has access to file
    if not user.is_admin and not user.is_moderator and file.owner_id != user.id:
        await log_api_request(Request, status.HTTP_403_FORBIDDEN, user.id, db)
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file
    db.delete(file)
    db.commit()
    
    await log_api_request(Request, status.HTTP_200_OK, user.id, db)
    
    return {"message": "File deleted successfully"}