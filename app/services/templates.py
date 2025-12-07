"""
KAPCI WhatsApp AI Agent - Message Templates
Bilingual Templates (Arabic + English)
"""
from typing import Optional
from app.models import Ticket, TicketStatus


class MessageTemplates:
    """Message Templates Manager"""
    
    # ==========================================
    # GREETING & MENU
    # ==========================================
    
    GREETING = {
        'ar': """مرحباً! 👋 أنا مساعد كابسي الذكي.

كيف يمكنني مساعدتك اليوم؟

1️⃣ تقديم شكوى منتج
2️⃣ متابعة شكوى سابقة
3️⃣ المساعدة""",
        
        'en': """Hello! 👋 I'm KAPCI AI Assistant.

How can I help you today?

1️⃣ Submit Product Complaint
2️⃣ Track Existing Complaint
3️⃣ Help"""
    }
    
    # ==========================================
    # DATA COLLECTION
    # ==========================================
    
    ASK_PRODUCT = {
        'ar': """📦 من فضلك أخبرني عن المنتج المُشتكى منه:

• اسم المنتج
• تاريخ الشراء (إن أمكن)

مثال: "طلاء أبيض 10 لتر، اشتريته الأسبوع الماضي" """,
        
        'en': """📦 Please tell me about the product:

• Product name
• Purchase date (if known)

Example: "White paint 10L, bought last week" """
    }
    
    ASK_ISSUE = {
        'ar': """📝 شكراً! الآن من فضلك اشرح المشكلة بالتفصيل:

ما المشكلة التي واجهتها مع هذا المنتج؟""",
        
        'en': """📝 Thanks! Now please describe the issue in detail:

What problem did you experience with this product?"""
    }
    
    ASK_PHOTOS = {
        'ar': """📷 هل تريد إرسال صور للمشكلة؟

يمكنك إرسال صور الآن، أو اكتب "تخطي" للمتابعة بدون صور.""",
        
        'en': """📷 Would you like to send photos of the issue?

You can send photos now, or type "skip" to continue without photos."""
    }
    
    # ==========================================
    # CONFIRMATION
    # ==========================================
    
    CONFIRM_DATA = {
        'ar': """📋 ملخص الشكوى:

🏭 المنتج: {product}
❌ المشكلة: {issue}

هل هذه المعلومات صحيحة؟
✅ نعم - لإرسال الشكوى
❌ لا - لتعديل المعلومات""",
        
        'en': """📋 Complaint Summary:

🏭 Product: {product}
❌ Issue: {issue}

Is this information correct?
✅ Yes - to submit complaint
❌ No - to edit information"""
    }
    
    CONFIRM_PROMPT = {
        'ar': """من فضلك أجب بـ:
✅ نعم - لتأكيد الشكوى
❌ لا - لتعديل المعلومات""",
        
        'en': """Please answer:
✅ Yes - to confirm complaint
❌ No - to edit information"""
    }
    
    # ==========================================
    # TICKET CREATED
    # ==========================================
    
    TICKET_CREATED = {
        'ar': """✅ تم إنشاء الشكوى بنجاح!

🎫 رقم التذكرة: {ticket_number}

سيقوم فريقنا الفني بمراجعة شكواك خلال 48 ساعة.
سنُبلغك بالنتيجة عبر هذه المحادثة.

شكراً لتواصلك معنا! 🙏""",
        
        'en': """✅ Complaint submitted successfully!

🎫 Ticket Number: {ticket_number}

Our technical team will review your complaint within 48 hours.
We'll notify you of the result through this chat.

Thank you for contacting us! 🙏"""
    }
    
    # ==========================================
    # TICKET STATUS
    # ==========================================
    
    TICKET_STATUS = {
        'ar': """📊 حالة الشكوى

🎫 رقم التذكرة: {ticket_number}
📅 تاريخ الإنشاء: {created_date}
📍 الحالة: {status}
🏭 المنتج: {product}

{extra_info}""",
        
        'en': """📊 Complaint Status

🎫 Ticket Number: {ticket_number}
📅 Created: {created_date}
📍 Status: {status}
🏭 Product: {product}

{extra_info}"""
    }
    
    STATUS_MAP = {
        'ar': {
            'pending_review': '⏳ قيد المراجعة الفنية',
            'under_review': '🔍 تحت المراجعة',
            'approved': '✅ تمت الموافقة',
            'rejected': '❌ مرفوض',
            'pending_finance': '💰 قيد معالجة الاسترداد',
            'finance_approved': '💰 تمت الموافقة على الاسترداد',
            'pending_inventory': '📦 قيد تجهيز البديل',
            'inventory_prepared': '📦 تم تجهيز البديل',
            'in_delivery': '🚚 في الطريق',
            'completed': '✅ مكتمل'
        },
        'en': {
            'pending_review': '⏳ Pending Technical Review',
            'under_review': '🔍 Under Review',
            'approved': '✅ Approved',
            'rejected': '❌ Rejected',
            'pending_finance': '💰 Processing Refund',
            'finance_approved': '💰 Refund Approved',
            'pending_inventory': '📦 Preparing Replacement',
            'inventory_prepared': '📦 Replacement Ready',
            'in_delivery': '🚚 In Delivery',
            'completed': '✅ Completed'
        }
    }
    
    # ==========================================
    # NOTIFICATIONS
    # ==========================================
    
    TICKET_REJECTED = {
        'ar': """❌ تحديث بخصوص شكواك

🎫 رقم التذكرة: {ticket_number}

بعد المراجعة الفنية، تبين أنه لا توجد مشكلة في المنتج.

📝 السبب: {reason}

إذا كان لديك استفسار أو معلومات إضافية، نحن هنا لمساعدتك.""",
        
        'en': """❌ Update on Your Complaint

🎫 Ticket Number: {ticket_number}

After technical review, no product issue was found.

📝 Reason: {reason}

If you have questions or additional information, we're here to help."""
    }
    
    TICKET_APPROVED_REFUND = {
        'ar': """✅ أخبار سارة!

🎫 رقم التذكرة: {ticket_number}

تمت الموافقة على شكواك! 🎉

💰 سيتم معالجة استرداد المبلغ خلال 3-5 أيام عمل.
سيتم إيداع المبلغ في حسابك المسجل لدينا.

شكراً لصبرك! 🙏""",
        
        'en': """✅ Good News!

🎫 Ticket Number: {ticket_number}

Your complaint has been approved! 🎉

💰 Refund will be processed within 3-5 business days.
The amount will be credited to your registered account.

Thank you for your patience! 🙏"""
    }
    
    TICKET_APPROVED_REPLACEMENT = {
        'ar': """✅ أخبار سارة!

🎫 رقم التذكرة: {ticket_number}

تمت الموافقة على شكواك! 🎉

📦 سيتم إرسال منتج بديل إليك قريباً.
سنُبلغك برقم التتبع عند الشحن.

شكراً لصبرك! 🙏""",
        
        'en': """✅ Good News!

🎫 Ticket Number: {ticket_number}

Your complaint has been approved! 🎉

📦 A replacement product will be sent to you soon.
We'll notify you with tracking information when shipped.

Thank you for your patience! 🙏"""
    }
    
    # ==========================================
    # MISC
    # ==========================================
    
    NO_TICKETS = {
        'ar': """📭 لم يتم العثور على شكاوى سابقة.

لتقديم شكوى جديدة، اكتب 1 أو "شكوى" """,
        
        'en': """📭 No previous complaints found.

To submit a new complaint, type 1 or "complaint" """
    }
    
    UNKNOWN = {
        'ar': """عذراً، لم أفهم طلبك. 🤔

اختر من القائمة:
1️⃣ شكوى جديدة
2️⃣ متابعة شكوى
3️⃣ المساعدة""",
        
        'en': """Sorry, I didn't understand. 🤔

Choose from the menu:
1️⃣ New Complaint
2️⃣ Track Complaint
3️⃣ Help"""
    }
    
    HELP = {
        'ar': """📖 المساعدة

أنا مساعد كابسي الذكي، يمكنني مساعدتك في:

1️⃣ تقديم شكوى منتج - إذا واجهت مشكلة مع أحد منتجاتنا
2️⃣ متابعة شكوى - للاستعلام عن حالة شكوى سابقة

الخطوات:
• أرسل "1" لتقديم شكوى
• سأطلب منك معلومات المنتج والمشكلة
• سيراجع فريقنا الفني خلال 48 ساعة
• سنُبلغك بالنتيجة

هل تريد تقديم شكوى الآن؟""",
        
        'en': """📖 Help

I'm KAPCI AI Assistant, I can help you with:

1️⃣ Submit Complaint - If you have an issue with our products
2️⃣ Track Complaint - To check status of existing complaint

Steps:
• Send "1" to submit a complaint
• I'll ask for product info and issue details
• Our team will review within 48 hours
• We'll notify you of the result

Would you like to submit a complaint now?"""
    }
    
    THANKS_RESPONSE = {
        'ar': """شكراً لتواصلك معنا! 🙏

هل هناك شيء آخر يمكنني مساعدتك به؟""",
        
        'en': """Thank you for contacting us! 🙏

Is there anything else I can help you with?"""
    }
    
    CANCELLED = {
        'ar': """تم إلغاء العملية. ✋

إذا احتجت المساعدة، أنا هنا!""",
        
        'en': """Operation cancelled. ✋

If you need help, I'm here!"""
    }
    
    RESTART = {
        'ar': """لا مشكلة، لنبدأ من جديد.""",
        'en': """No problem, let's start again."""
    }
    
    REMINDER = {
        'ar': {
            'pending_review': """⏰ تذكير: شكواك رقم {ticket_number} قيد المراجعة.
سيقوم فريقنا بالرد قريباً.""",
            'awaiting_customer': """⏰ تذكير: نحتاج ردك على شكوى رقم {ticket_number}."""
        },
        'en': {
            'pending_review': """⏰ Reminder: Your complaint {ticket_number} is under review.
Our team will respond soon.""",
            'awaiting_customer': """⏰ Reminder: We need your response for ticket {ticket_number}."""
        }
    }
    
    # ==========================================
    # GETTER METHODS
    # ==========================================
    
    def get_greeting(self, lang: str = 'ar') -> str:
        return self.GREETING.get(lang, self.GREETING['ar'])
    
    def get_ask_product(self, lang: str = 'ar') -> str:
        return self.ASK_PRODUCT.get(lang, self.ASK_PRODUCT['ar'])
    
    def get_ask_issue(self, lang: str = 'ar') -> str:
        return self.ASK_ISSUE.get(lang, self.ASK_ISSUE['ar'])
    
    def get_ask_photos(self, lang: str = 'ar') -> str:
        return self.ASK_PHOTOS.get(lang, self.ASK_PHOTOS['ar'])
    
    def get_confirm_data(self, product: str, issue: str, lang: str = 'ar') -> str:
        template = self.CONFIRM_DATA.get(lang, self.CONFIRM_DATA['ar'])
        return template.format(product=product, issue=issue)
    
    def get_confirm_prompt(self, lang: str = 'ar') -> str:
        return self.CONFIRM_PROMPT.get(lang, self.CONFIRM_PROMPT['ar'])
    
    def get_ticket_created(self, ticket_number: str, lang: str = 'ar') -> str:
        template = self.TICKET_CREATED.get(lang, self.TICKET_CREATED['ar'])
        return template.format(ticket_number=ticket_number)
    
    def get_ticket_status(self, ticket: Ticket, lang: str = 'ar') -> str:
        template = self.TICKET_STATUS.get(lang, self.TICKET_STATUS['ar'])
        status_map = self.STATUS_MAP.get(lang, self.STATUS_MAP['ar'])
        
        extra_info = ""
        if ticket.compensation_type == 'refund':
            extra_info = "💰 نوع التعويض: استرداد مبلغ" if lang == 'ar' else "💰 Compensation: Refund"
        elif ticket.compensation_type == 'replacement':
            extra_info = "📦 نوع التعويض: استبدال منتج" if lang == 'ar' else "📦 Compensation: Replacement"
        
        return template.format(
            ticket_number=ticket.ticket_number,
            created_date=ticket.created_at.strftime('%Y-%m-%d'),
            status=status_map.get(ticket.status, ticket.status),
            product=ticket.product_name or '-',
            extra_info=extra_info
        )
    
    def get_no_tickets(self, lang: str = 'ar') -> str:
        return self.NO_TICKETS.get(lang, self.NO_TICKETS['ar'])
    
    def get_unknown(self, lang: str = 'ar') -> str:
        return self.UNKNOWN.get(lang, self.UNKNOWN['ar'])
    
    def get_help(self, lang: str = 'ar') -> str:
        return self.HELP.get(lang, self.HELP['ar'])
    
    def get_thanks_response(self, lang: str = 'ar') -> str:
        return self.THANKS_RESPONSE.get(lang, self.THANKS_RESPONSE['ar'])
    
    def get_cancelled(self, lang: str = 'ar') -> str:
        return self.CANCELLED.get(lang, self.CANCELLED['ar'])
    
    def get_restart(self, lang: str = 'ar') -> str:
        return self.RESTART.get(lang, self.RESTART['ar'])
    
    def get_ticket_rejected(self, ticket_number: str, reason: str, lang: str = 'ar') -> str:
        template = self.TICKET_REJECTED.get(lang, self.TICKET_REJECTED['ar'])
        return template.format(ticket_number=ticket_number, reason=reason)
    
    def get_ticket_approved_refund(self, ticket_number: str, lang: str = 'ar') -> str:
        template = self.TICKET_APPROVED_REFUND.get(lang, self.TICKET_APPROVED_REFUND['ar'])
        return template.format(ticket_number=ticket_number)
    
    def get_ticket_approved_replacement(self, ticket_number: str, lang: str = 'ar') -> str:
        template = self.TICKET_APPROVED_REPLACEMENT.get(lang, self.TICKET_APPROVED_REPLACEMENT['ar'])
        return template.format(ticket_number=ticket_number)
    
    def get_reminder(self, ticket_number: str, reminder_type: str, lang: str = 'ar') -> str:
        reminders = self.REMINDER.get(lang, self.REMINDER['ar'])
        template = reminders.get(reminder_type, reminders.get('pending_review'))
        return template.format(ticket_number=ticket_number)
