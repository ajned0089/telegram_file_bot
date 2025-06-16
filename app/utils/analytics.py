"""
Analytics utilities for the bot.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import User, File, FileDownload, Category

def get_user_growth(db: Session, days: int = 30) -> List[Tuple[str, int]]:
    """Get user growth over time."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query users created per day
    result = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).group_by(
        func.date(User.created_at)
    ).all()
    
    # Convert to list of tuples (date_str, count)
    return [(str(date), count) for date, count in result]

def get_file_uploads(db: Session, days: int = 30) -> List[Tuple[str, int]]:
    """Get file uploads over time."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query files uploaded per day
    result = db.query(
        func.date(File.upload_date).label('date'),
        func.count(File.id).label('count')
    ).filter(
        File.upload_date >= start_date,
        File.upload_date <= end_date
    ).group_by(
        func.date(File.upload_date)
    ).all()
    
    # Convert to list of tuples (date_str, count)
    return [(str(date), count) for date, count in result]

def get_file_downloads(db: Session, days: int = 30) -> List[Tuple[str, int]]:
    """Get file downloads over time."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query file downloads per day
    result = db.query(
        func.date(FileDownload.download_date).label('date'),
        func.count(FileDownload.id).label('count')
    ).filter(
        FileDownload.download_date >= start_date,
        FileDownload.download_date <= end_date
    ).group_by(
        func.date(FileDownload.download_date)
    ).all()
    
    # Convert to list of tuples (date_str, count)
    return [(str(date), count) for date, count in result]

def get_popular_categories(db: Session, limit: int = 5) -> List[Tuple[str, int]]:
    """Get most popular categories."""
    # Query categories with most files
    result = db.query(
        Category.name_en,
        func.count(File.id).label('count')
    ).join(
        File, File.category_id == Category.id
    ).group_by(
        Category.id
    ).order_by(
        func.count(File.id).desc()
    ).limit(limit).all()
    
    return [(name, count) for name, count in result]

def get_popular_file_types(db: Session, limit: int = 5) -> List[Tuple[str, int]]:
    """Get most popular file types."""
    # Query file types with most files
    result = db.query(
        File.file_type,
        func.count(File.id).label('count')
    ).group_by(
        File.file_type
    ).order_by(
        func.count(File.id).desc()
    ).limit(limit).all()
    
    return [(file_type, count) for file_type, count in result]

def get_user_activity_heatmap(db: Session) -> Dict[str, Dict[str, int]]:
    """Get user activity heatmap (day of week, hour of day)."""
    # Query user activity by day of week and hour of day
    result = db.query(
        func.strftime('%w', User.last_activity).label('day_of_week'),
        func.strftime('%H', User.last_activity).label('hour_of_day'),
        func.count(User.id).label('count')
    ).filter(
        User.last_activity.isnot(None)
    ).group_by(
        'day_of_week', 'hour_of_day'
    ).all()
    
    # Convert to dictionary
    heatmap = {}
    for day, hour, count in result:
        if day not in heatmap:
            heatmap[day] = {}
        heatmap[day][hour] = count
    
    return heatmap

def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """Get dashboard statistics."""
    # Get total counts
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_files = db.query(func.count(File.id)).scalar() or 0
    total_downloads = db.query(func.sum(File.download_count)).scalar() or 0
    
    # Get active users (last 7 days)
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(func.count(User.id)).filter(User.last_activity >= cutoff_date).scalar() or 0
    
    # Get total storage used
    total_size = db.query(func.sum(File.file_size)).scalar() or 0
    
    # Get recent users
    recent_users = db.query(User).order_by(User.last_activity.desc()).limit(5).all()
    
    # Get recent files
    recent_files = db.query(File).order_by(File.upload_date.desc()).limit(5).all()
    
    # Get user growth (last 30 days)
    user_growth = get_user_growth(db, 30)
    
    # Get file uploads (last 30 days)
    file_uploads = get_file_uploads(db, 30)
    
    # Get file downloads (last 30 days)
    file_downloads = get_file_downloads(db, 30)
    
    # Get popular categories
    popular_categories = get_popular_categories(db)
    
    # Get popular file types
    popular_file_types = get_popular_file_types(db)
    
    return {
        "total_users": total_users,
        "total_files": total_files,
        "total_downloads": total_downloads,
        "active_users": active_users,
        "total_size": total_size,
        "recent_users": recent_users,
        "recent_files": recent_files,
        "user_growth": user_growth,
        "file_uploads": file_uploads,
        "file_downloads": file_downloads,
        "popular_categories": popular_categories,
        "popular_file_types": popular_file_types
    }