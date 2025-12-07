"""
KAPCI WhatsApp AI Agent - Validation Utilities
"""
import re
from typing import Optional, Tuple


class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Egyptian phone number
        Returns (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"
        
        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Egyptian phone patterns
        patterns = [
            r'^\+20[0-9]{10}$',      # +201xxxxxxxxx
            r'^20[0-9]{10}$',         # 201xxxxxxxxx
            r'^0[0-9]{10}$',          # 01xxxxxxxxx
            r'^[0-9]{10}$'            # 1xxxxxxxxx
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned):
                return True, None
        
        return False, "Invalid Egyptian phone number"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        if not email:
            return True, None  # Email is optional
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            return True, None
        
        return False, "Invalid email address"
    
    @staticmethod
    def validate_ticket_number(ticket_num: str) -> Tuple[bool, Optional[str]]:
        """Validate ticket number format"""
        if not ticket_num:
            return False, "Ticket number is required"
        
        pattern = r'^TKT-\d{4}-\d{5}$'
        
        if re.match(pattern, ticket_num):
            return True, None
        
        return False, "Invalid ticket number format (expected: TKT-YYYY-XXXXX)"
    
    @staticmethod
    def validate_text_length(text: str, min_len: int = 1, max_len: int = 1000,
                           field_name: str = "Text") -> Tuple[bool, Optional[str]]:
        """Validate text length"""
        if not text:
            if min_len > 0:
                return False, f"{field_name} is required"
            return True, None
        
        if len(text) < min_len:
            return False, f"{field_name} must be at least {min_len} characters"
        
        if len(text) > max_len:
            return False, f"{field_name} must not exceed {max_len} characters"
        
        return True, None
    
    @staticmethod
    def validate_product_info(product_name: str) -> Tuple[bool, Optional[str]]:
        """Validate product information"""
        if not product_name or len(product_name.strip()) < 3:
            return False, "Please provide a valid product name (minimum 3 characters)"
        
        if len(product_name) > 200:
            return False, "Product name is too long"
        
        return True, None
    
    @staticmethod
    def validate_issue_description(description: str) -> Tuple[bool, Optional[str]]:
        """Validate issue description"""
        if not description or len(description.strip()) < 10:
            return False, "Please describe the issue in more detail (minimum 10 characters)"
        
        if len(description) > 2000:
            return False, "Issue description is too long"
        
        return True, None
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>{}]', '', text)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized
    
    @staticmethod
    def is_spam(text: str) -> bool:
        """Basic spam detection"""
        if not text:
            return False
        
        # Check for excessive repetition
        if len(set(text)) < 3 and len(text) > 10:
            return True
        
        # Check for excessive caps
        if len(text) > 20 and text.isupper():
            return True
        
        # Check for spam keywords
        spam_keywords = ['click here', 'free money', 'winner', 'congratulations']
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in spam_keywords):
            return True
        
        return False


# Singleton instance
validator = Validator()
