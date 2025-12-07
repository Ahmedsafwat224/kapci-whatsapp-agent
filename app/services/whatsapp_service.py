"""
KAPCI WhatsApp AI Agent - WhatsApp Service
WhatsApp Business API Integration
"""
import requests
import json
import hashlib
import hmac
from typing import Dict, List, Optional
from datetime import datetime
import os


class WhatsAppService:
    """WhatsApp Business API Service"""
    
    def __init__(self, app=None):
        """Initialize WhatsApp Service"""
        self.api_url = None
        self.phone_number_id = None
        self.access_token = None
        self.verify_token = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app config"""
        self.api_url = app.config.get('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
        self.phone_number_id = app.config.get('WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = app.config.get('WHATSAPP_ACCESS_TOKEN', '')
        self.verify_token = app.config.get('WHATSAPP_VERIFY_TOKEN', 'kapci_verify_token')
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription from WhatsApp
        
        Args:
            mode: Subscription mode
            token: Verify token
            challenge: Challenge string
            
        Returns:
            Challenge string if valid, None otherwise
        """
        if mode == 'subscribe' and token == self.verify_token:
            return challenge
        return None
    
    def parse_incoming_message(self, payload: Dict) -> Optional[Dict]:
        """
        Parse incoming webhook payload from WhatsApp
        
        Args:
            payload: Webhook payload
            
        Returns:
            Parsed message dict or None
        """
        try:
            entry = payload.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            messages = value.get('messages', [])
            if not messages:
                return None
            
            message = messages[0]
            contact = value.get('contacts', [{}])[0]
            
            parsed = {
                'message_id': message.get('id'),
                'from': message.get('from'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type'),
                'contact_name': contact.get('profile', {}).get('name'),
            }
            
            # Parse based on message type
            msg_type = message.get('type')
            
            if msg_type == 'text':
                parsed['content'] = message.get('text', {}).get('body', '')
            
            elif msg_type == 'image':
                img = message.get('image', {})
                parsed['content'] = img.get('caption', '')
                parsed['media_id'] = img.get('id')
                parsed['media_mime'] = img.get('mime_type')
            
            elif msg_type == 'document':
                doc = message.get('document', {})
                parsed['content'] = doc.get('caption', '')
                parsed['media_id'] = doc.get('id')
                parsed['media_mime'] = doc.get('mime_type')
                parsed['filename'] = doc.get('filename')
            
            elif msg_type == 'interactive':
                interactive = message.get('interactive', {})
                int_type = interactive.get('type')
                if int_type == 'button_reply':
                    parsed['content'] = interactive.get('button_reply', {}).get('title', '')
                    parsed['button_id'] = interactive.get('button_reply', {}).get('id')
                elif int_type == 'list_reply':
                    parsed['content'] = interactive.get('list_reply', {}).get('title', '')
                    parsed['list_id'] = interactive.get('list_reply', {}).get('id')
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None
    
    def send_text_message(self, to: str, text: str) -> Dict:
        """
        Send text message
        
        Args:
            to: Recipient phone number
            text: Message text
            
        Returns:
            API response
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'text',
            'text': {
                'preview_url': False,
                'body': text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return {'error': str(e)}
    
    def send_template_message(self, to: str, template_name: str, 
                             language: str = 'ar', 
                             components: List[Dict] = None) -> Dict:
        """
        Send template message
        
        Args:
            to: Recipient phone number
            template_name: Template name
            language: Language code
            components: Template components
            
        Returns:
            API response
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {
                    'code': language
                }
            }
        }
        
        if components:
            payload['template']['components'] = components
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending template: {e}")
            return {'error': str(e)}
    
    def send_interactive_buttons(self, to: str, body: str, 
                                buttons: List[Dict],
                                header: str = None,
                                footer: str = None) -> Dict:
        """
        Send interactive button message
        
        Args:
            to: Recipient phone number
            body: Message body
            buttons: List of buttons (max 3)
            header: Optional header text
            footer: Optional footer text
            
        Returns:
            API response
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        interactive = {
            'type': 'button',
            'body': {
                'text': body
            },
            'action': {
                'buttons': [
                    {
                        'type': 'reply',
                        'reply': {
                            'id': btn.get('id'),
                            'title': btn.get('title')
                        }
                    } for btn in buttons[:3]  # Max 3 buttons
                ]
            }
        }
        
        if header:
            interactive['header'] = {'type': 'text', 'text': header}
        if footer:
            interactive['footer'] = {'text': footer}
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'interactive',
            'interactive': interactive
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending interactive: {e}")
            return {'error': str(e)}
    
    def send_interactive_list(self, to: str, body: str,
                             button_text: str,
                             sections: List[Dict],
                             header: str = None,
                             footer: str = None) -> Dict:
        """
        Send interactive list message
        
        Args:
            to: Recipient phone number
            body: Message body
            button_text: Button text
            sections: List of sections with rows
            header: Optional header
            footer: Optional footer
            
        Returns:
            API response
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        interactive = {
            'type': 'list',
            'body': {
                'text': body
            },
            'action': {
                'button': button_text,
                'sections': sections
            }
        }
        
        if header:
            interactive['header'] = {'type': 'text', 'text': header}
        if footer:
            interactive['footer'] = {'text': footer}
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'interactive',
            'interactive': interactive
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending list: {e}")
            return {'error': str(e)}
    
    def download_media(self, media_id: str) -> Optional[bytes]:
        """
        Download media file from WhatsApp
        
        Args:
            media_id: Media ID
            
        Returns:
            Media bytes or None
        """
        # First get media URL
        url = f"{self.api_url}/{media_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            media_url = response.json().get('url')
            
            if media_url:
                # Download the actual media
                media_response = requests.get(media_url, headers=headers)
                return media_response.content
        except Exception as e:
            print(f"Error downloading media: {e}")
        
        return None
    
    def mark_as_read(self, message_id: str) -> Dict:
        """
        Mark message as read
        
        Args:
            message_id: Message ID
            
        Returns:
            API response
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'status': 'read',
            'message_id': message_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            return {'error': str(e)}


# Singleton instance
whatsapp_service = WhatsAppService()
