"""
KAPCI WhatsApp AI Agent - Utility Helpers
"""
import re
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json


def generate_hash(data: str) -> str:
    """Generate SHA256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def sanitize_phone(phone: str) -> str:
    """
    Sanitize and format phone number
    Converts to E.164 format for Egypt
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle Egyptian numbers
    if digits.startswith('20'):
        return '+' + digits
    elif digits.startswith('0'):
        return '+20' + digits[1:]
    elif len(digits) == 10:
        return '+20' + digits
    
    return '+' + digits


def format_datetime(dt: datetime, lang: str = 'en') -> str:
    """Format datetime for display"""
    if lang == 'ar':
        return dt.strftime('%Y/%m/%d %H:%M')
    return dt.strftime('%d %b %Y, %H:%M')


def format_date(dt: datetime, lang: str = 'en') -> str:
    """Format date for display"""
    if lang == 'ar':
        return dt.strftime('%Y/%m/%d')
    return dt.strftime('%d %b %Y')


def time_ago(dt: datetime, lang: str = 'en') -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if lang == 'ar':
        if seconds < 60:
            return 'الآن'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'منذ {minutes} دقيقة'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'منذ {hours} ساعة'
        else:
            days = int(seconds / 86400)
            return f'منذ {days} يوم'
    else:
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minutes ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hours ago'
        else:
            days = int(seconds / 86400)
            return f'{days} days ago'


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters"""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date from various formats"""
    formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d %b %Y',
        '%B %d, %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def mask_phone(phone: str) -> str:
    """Mask phone number for privacy"""
    if len(phone) < 8:
        return phone
    return phone[:4] + '****' + phone[-3:]


def calculate_business_days(start_date: datetime, num_days: int) -> datetime:
    """Calculate date after business days (excluding weekends)"""
    current_date = start_date
    days_added = 0
    
    while days_added < num_days:
        current_date += timedelta(days=1)
        # Skip Friday and Saturday (Egyptian weekend)
        if current_date.weekday() not in (4, 5):
            days_added += 1
    
    return current_date


def get_greeting_by_time(lang: str = 'ar') -> str:
    """Get appropriate greeting based on time of day"""
    hour = datetime.now().hour
    
    if lang == 'ar':
        if 5 <= hour < 12:
            return 'صباح الخير'
        elif 12 <= hour < 17:
            return 'مساء الخير'
        else:
            return 'مساء الخير'
    else:
        if 5 <= hour < 12:
            return 'Good morning'
        elif 12 <= hour < 17:
            return 'Good afternoon'
        else:
            return 'Good evening'


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        self.requests[key].append(now)
        return True


# Singleton rate limiter
rate_limiter = RateLimiter()
