"""
KAPCI WhatsApp AI Agent - AI Service
Intent Classification, Entity Extraction, Response Generation
"""
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class AIService:
    """AI Service for NLP tasks"""
    
    # Intent keywords (Arabic + English)
    INTENT_KEYWORDS = {
        'greeting': [
            'hello', 'hi', 'hey', 'good morning', 'good evening',
            'السلام عليكم', 'مرحبا', 'اهلا', 'صباح الخير', 'مساء الخير', 'هلا'
        ],
        'new_complaint': [
            'complaint', 'problem', 'issue', 'defect', 'broken', 'damaged', 'wrong',
            'شكوى', 'مشكلة', 'عطل', 'خراب', 'تالف', 'معيب', 'غلط', 'مش شغال',
            '1', 'one', 'واحد'
        ],
        'check_status': [
            'status', 'track', 'follow up', 'where', 'check',
            'متابعة', 'حالة', 'تتبع', 'فين', 'وصلت فين',
            '2', 'two', 'اتنين'
        ],
        'provide_info': [
            # This is detected by context, not keywords
        ],
        'send_photo': [
            'photo', 'image', 'picture', 'attached',
            'صورة', 'صور'
        ],
        'confirm_yes': [
            'yes', 'yeah', 'yep', 'ok', 'okay', 'correct', 'right', 'confirm', 'sure',
            'نعم', 'اه', 'ايه', 'ايوه', 'صح', 'تمام', 'موافق', 'اكيد', 'ماشي'
        ],
        'confirm_no': [
            'no', 'nope', 'wrong', 'incorrect', 'change', 'edit',
            'لا', 'لأ', 'غلط', 'مش صح', 'تعديل', 'غير'
        ],
        'skip': [
            'skip', 'no photo', 'no photos', 'none', 'nothing', 'done',
            'تخطي', 'مفيش', 'تم', 'بدون', 'لا صور', 'مش هبعت'
        ],
        'cancel': [
            'cancel', 'stop', 'quit', 'exit', 'bye',
            'الغاء', 'الغي', 'وقف', 'خلاص', 'مع السلامة'
        ],
        'help': [
            'help', 'assist', 'support', 'how',
            'مساعدة', 'ساعدني', 'ازاي', 'كيف'
        ],
        'thanks': [
            'thanks', 'thank you', 'thx',
            'شكرا', 'متشكر'
        ]
    }
    
    # Entity patterns
    ENTITY_PATTERNS = {
        'ticket_number': r'TKT-\d{4}-\d{5}',
        'phone': r'(?:\+?20)?(?:0)?1[0125]\d{8}',
        'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
        'quantity': r'(?:quantity|qty|كمية|عدد)[:\s]*(\d+)',
        'email': r'[\w\.-]+@[\w\.-]+\.\w+'
    }
    
    def __init__(self, llm_provider=None):
        """Initialize AI Service"""
        self.llm_provider = llm_provider
    
    def classify_intent(self, message: str, current_step: str = 'idle') -> str:
        """
        Classify user intent based on message content and current conversation step
        
        Args:
            message: User message text
            current_step: Current conversation state
            
        Returns:
            Detected intent string
        """
        message_lower = message.lower().strip()
        
        # Context-based classification for data collection steps
        if current_step in ['collecting_product', 'collecting_issue', 'collecting_name', 
                           'collecting_purchase_date', 'collecting_quantity']:
            return 'provide_info'
        
        # Photo collection step
        if current_step == 'collecting_photos':
            # Check for skip intent
            for keyword in self.INTENT_KEYWORDS['skip']:
                if keyword in message_lower:
                    return 'skip'
            # Check if it's a media message (would be handled by message type)
            return 'provide_info'
        
        # Confirmation step
        if current_step == 'confirming_data':
            for keyword in self.INTENT_KEYWORDS['confirm_yes']:
                if keyword in message_lower:
                    return 'confirm_yes'
            for keyword in self.INTENT_KEYWORDS['confirm_no']:
                if keyword in message_lower:
                    return 'confirm_no'
            return 'unknown'
        
        # General intent classification
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return 'unknown'
    
    def extract_entities(self, message: str) -> Dict[str, any]:
        """
        Extract entities from message
        
        Args:
            message: User message text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Ticket number
        ticket_match = re.search(self.ENTITY_PATTERNS['ticket_number'], message)
        if ticket_match:
            entities['ticket_number'] = ticket_match.group()
        
        # Phone number
        phone_match = re.search(self.ENTITY_PATTERNS['phone'], message)
        if phone_match:
            entities['phone'] = phone_match.group()
        
        # Date
        date_match = re.search(self.ENTITY_PATTERNS['date'], message)
        if date_match:
            entities['date'] = date_match.group()
        
        # Quantity
        qty_match = re.search(self.ENTITY_PATTERNS['quantity'], message, re.IGNORECASE)
        if qty_match:
            entities['quantity'] = int(qty_match.group(1))
        
        # Email
        email_match = re.search(self.ENTITY_PATTERNS['email'], message)
        if email_match:
            entities['email'] = email_match.group()
        
        return entities
    
    def detect_language(self, message: str) -> str:
        """
        Detect message language (Arabic or English)
        
        Args:
            message: User message text
            
        Returns:
            Language code ('ar' or 'en')
        """
        # Arabic Unicode range
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', message))
        english_chars = len(re.findall(r'[a-zA-Z]', message))
        
        if arabic_chars > english_chars:
            return 'ar'
        return 'en'
    
    def analyze_sentiment(self, message: str) -> str:
        """
        Simple sentiment analysis
        
        Args:
            message: User message text
            
        Returns:
            Sentiment ('positive', 'negative', 'neutral')
        """
        message_lower = message.lower()
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'angry', 'frustrated',
            'سيء', 'وحش', 'زعلان', 'متضايق', 'غضبان'
        ]
        
        positive_words = [
            'good', 'great', 'excellent', 'thanks', 'happy', 'satisfied',
            'كويس', 'ممتاز', 'شكرا', 'مبسوط', 'راضي'
        ]
        
        neg_count = sum(1 for word in negative_words if word in message_lower)
        pos_count = sum(1 for word in positive_words if word in message_lower)
        
        if neg_count > pos_count:
            return 'negative'
        elif pos_count > neg_count:
            return 'positive'
        return 'neutral'
    
    def suggest_issue_category(self, description: str) -> str:
        """
        Suggest issue category based on description
        
        Args:
            description: Issue description text
            
        Returns:
            Suggested category
        """
        desc_lower = description.lower()
        
        categories = {
            'quality': ['quality', 'defect', 'broken', 'damaged', 'جودة', 'معيب', 'مكسور'],
            'wrong_product': ['wrong', 'different', 'not what', 'غلط', 'مختلف'],
            'missing_parts': ['missing', 'incomplete', 'ناقص', 'مش كامل'],
            'not_working': ['not working', 'doesnt work', 'مش شغال', 'مش بيشتغل'],
            'expired': ['expired', 'old', 'منتهي', 'قديم'],
            'packaging': ['packaging', 'box', 'تغليف', 'علبة']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return category
        
        return 'other'


# Singleton instance
ai_service = AIService()
