"""
KAPCI WhatsApp AI Agent - Service Tests
"""
import pytest
from app.services.ai_service import AIService


class TestAIService:
    """Test AI Service"""
    
    def setup_method(self):
        """Setup test instance"""
        self.ai = AIService()
    
    def test_classify_greeting_english(self):
        """Test greeting classification in English"""
        assert self.ai.classify_intent('hello', 'idle') == 'greeting'
        assert self.ai.classify_intent('hi there', 'idle') == 'greeting'
        assert self.ai.classify_intent('hey', 'idle') == 'greeting'
    
    def test_classify_greeting_arabic(self):
        """Test greeting classification in Arabic"""
        assert self.ai.classify_intent('مرحبا', 'idle') == 'greeting'
        assert self.ai.classify_intent('السلام عليكم', 'idle') == 'greeting'
        assert self.ai.classify_intent('اهلا', 'idle') == 'greeting'
    
    def test_classify_new_complaint(self):
        """Test new complaint classification"""
        assert self.ai.classify_intent('1', 'idle') == 'new_complaint'
        assert self.ai.classify_intent('complaint', 'idle') == 'new_complaint'
        assert self.ai.classify_intent('شكوى', 'idle') == 'new_complaint'
        assert self.ai.classify_intent('مشكلة', 'idle') == 'new_complaint'
    
    def test_classify_check_status(self):
        """Test status check classification"""
        assert self.ai.classify_intent('2', 'idle') == 'check_status'
        assert self.ai.classify_intent('track', 'idle') == 'check_status'
        assert self.ai.classify_intent('متابعة', 'idle') == 'check_status'
    
    def test_classify_confirmation(self):
        """Test confirmation classification"""
        assert self.ai.classify_intent('yes', 'confirming_data') == 'confirm_yes'
        assert self.ai.classify_intent('نعم', 'confirming_data') == 'confirm_yes'
        assert self.ai.classify_intent('no', 'confirming_data') == 'confirm_no'
        assert self.ai.classify_intent('لا', 'confirming_data') == 'confirm_no'
    
    def test_classify_skip(self):
        """Test skip classification"""
        assert self.ai.classify_intent('skip', 'collecting_photos') == 'skip'
        assert self.ai.classify_intent('تخطي', 'collecting_photos') == 'skip'
    
    def test_context_aware_classification(self):
        """Test context-aware classification for data collection"""
        assert self.ai.classify_intent('some product', 'collecting_product') == 'provide_info'
        assert self.ai.classify_intent('the paint is bad', 'collecting_issue') == 'provide_info'
    
    def test_detect_language_arabic(self):
        """Test Arabic language detection"""
        assert self.ai.detect_language('مرحبا كيف حالك') == 'ar'
        assert self.ai.detect_language('أريد تقديم شكوى') == 'ar'
    
    def test_detect_language_english(self):
        """Test English language detection"""
        assert self.ai.detect_language('Hello how are you') == 'en'
        assert self.ai.detect_language('I want to submit a complaint') == 'en'
    
    def test_extract_ticket_number(self):
        """Test ticket number extraction"""
        entities = self.ai.extract_entities('My ticket is TKT-2024-12345')
        assert entities.get('ticket_number') == 'TKT-2024-12345'
    
    def test_suggest_issue_category(self):
        """Test issue category suggestion"""
        assert self.ai.suggest_issue_category('product is broken') == 'quality'
        assert self.ai.suggest_issue_category('wrong product delivered') == 'wrong_product'
        assert self.ai.suggest_issue_category('parts are missing') == 'missing_parts'
