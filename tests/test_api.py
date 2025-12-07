"""
KAPCI WhatsApp AI Agent - API Tests
"""
import pytest
import json


class TestChatAPI:
    """Test chat API endpoints"""
    
    def test_chat_endpoint(self, client):
        """Test basic chat endpoint"""
        response = client.post('/api/chat', json={
            'phone': '+201001234567',
            'message': 'Hello'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
        assert len(data['response']) > 0
    
    def test_chat_arabic(self, client):
        """Test Arabic message handling"""
        response = client.post('/api/chat', json={
            'phone': '+201001234567',
            'message': 'مرحبا'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
    
    def test_chat_empty_message(self, client):
        """Test empty message handling"""
        response = client.post('/api/chat', json={
            'phone': '+201001234567',
            'message': ''
        })
        
        assert response.status_code == 400
    
    def test_new_complaint_flow(self, client):
        """Test new complaint submission flow"""
        phone = '+201009999999'
        
        # Start with greeting
        response = client.post('/api/chat', json={
            'phone': phone,
            'message': '1'
        })
        assert response.status_code == 200
        
        # Provide product info
        response = client.post('/api/chat', json={
            'phone': phone,
            'message': 'KAPCI Paint 5L, bought yesterday'
        })
        assert response.status_code == 200
        
        # Provide issue
        response = client.post('/api/chat', json={
            'phone': phone,
            'message': 'Paint is too thick'
        })
        assert response.status_code == 200
        
        # Skip photos
        response = client.post('/api/chat', json={
            'phone': phone,
            'message': 'skip'
        })
        assert response.status_code == 200
        
        # Confirm
        response = client.post('/api/chat', json={
            'phone': phone,
            'message': 'yes'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'TKT-' in data['response']


class TestTicketAPI:
    """Test ticket API endpoints"""
    
    def test_get_tickets(self, client):
        """Test getting tickets list"""
        response = client.get('/api/tickets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tickets' in data
        assert isinstance(data['tickets'], list)
    
    def test_get_stats(self, client):
        """Test getting statistics"""
        response = client.get('/api/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'pending' in data
        assert 'approved' in data
        assert 'rejected' in data


class TestWebhookAPI:
    """Test WhatsApp webhook endpoints"""
    
    def test_webhook_verification(self, client):
        """Test webhook verification endpoint"""
        response = client.get('/api/webhook/whatsapp', query_string={
            'hub.mode': 'subscribe',
            'hub.verify_token': 'kapci_verify_token',
            'hub.challenge': 'test_challenge'
        })
        
        assert response.status_code == 200
        assert response.data.decode() == 'test_challenge'
    
    def test_webhook_verification_invalid(self, client):
        """Test webhook verification with invalid token"""
        response = client.get('/api/webhook/whatsapp', query_string={
            'hub.mode': 'subscribe',
            'hub.verify_token': 'wrong_token',
            'hub.challenge': 'test_challenge'
        })
        
        assert response.status_code == 403
