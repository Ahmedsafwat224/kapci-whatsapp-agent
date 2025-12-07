"""
KAPCI WhatsApp AI Agent - Utility Functions
"""
import re
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def normalize_phone(phone: str) -> str:
    """Normalize phone number to standard format"""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('20'):
        return f'+{digits}'
    elif digits.startswith('0'):
        return f'+20{digits[1:]}'
    elif len(digits) == 10:
        return f'+20{digits}'
    return f'+{digits}' if not phone.startswith('+') else phone


def validate_egypt_phone(phone: str) -> bool:
    """Validate Egyptian phone number"""
    pattern = r'^(\+?20|0)?1[0125]\d{8}$'
    normalized = re.sub(r'\D', '', phone)
    return bool(re.match(pattern, normalized))


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in various formats"""
    formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def truncate(text: str, length: int = 100) -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= length:
        return text or ''
    return text[:length].rsplit(' ', 1)[0] + '...'


def contains_arabic(text: str) -> bool:
    """Check if text contains Arabic characters"""
    return bool(re.search(r'[\u0600-\u06FF]', text))


def generate_token(length: int = 32) -> str:
    """Generate random secure token"""
    return uuid.uuid4().hex[:length]


def mask_phone(phone: str) -> str:
    """Mask phone number for display"""
    if not phone or len(phone) < 6:
        return '***'
    return phone[:3] + '***' + phone[-3:]


def validate_ticket_number(ticket_number: str) -> bool:
    """Validate ticket number format"""
    return bool(re.match(r'^TKT-\d{4}-\d{5}$', ticket_number))


def calculate_sla_deadline(created_at: datetime, hours: int = 48) -> datetime:
    """Calculate SLA deadline"""
    return created_at + timedelta(hours=hours)


def is_sla_breached(created_at: datetime, hours: int = 48) -> bool:
    """Check if SLA has been breached"""
    return datetime.utcnow() > calculate_sla_deadline(created_at, hours)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator for functions that may fail"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator
