"""
KAPCI WhatsApp AI Agent - External API Services
CRM, ERP, and Inventory System Integration
"""
import requests
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CRMService:
    """Customer Relationship Management API Integration"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or 'http://localhost:8001/api'
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_customer(self, phone: str) -> Optional[Dict]:
        """
        Get customer information from CRM
        
        Args:
            phone: Customer phone number
            
        Returns:
            Customer data dict or None
        """
        try:
            response = requests.get(
                f'{self.base_url}/customers/phone/{phone}',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"CRM API error: {e}")
            return None
    
    def get_customer_by_account(self, account_id: str) -> Optional[Dict]:
        """Get customer by KAPCI account ID"""
        try:
            response = requests.get(
                f'{self.base_url}/customers/account/{account_id}',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"CRM API error: {e}")
            return None
    
    def create_customer(self, data: Dict) -> Optional[Dict]:
        """Create new customer in CRM"""
        try:
            response = requests.post(
                f'{self.base_url}/customers',
                headers=self.headers,
                json=data,
                timeout=10
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"CRM API error: {e}")
            return None
    
    def update_customer(self, customer_id: str, data: Dict) -> Optional[Dict]:
        """Update customer information"""
        try:
            response = requests.put(
                f'{self.base_url}/customers/{customer_id}',
                headers=self.headers,
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"CRM API error: {e}")
            return None
    
    def log_interaction(self, customer_id: str, interaction: Dict) -> bool:
        """Log customer interaction"""
        try:
            response = requests.post(
                f'{self.base_url}/customers/{customer_id}/interactions',
                headers=self.headers,
                json=interaction,
                timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"CRM API error: {e}")
            return False


class ERPService:
    """ERP System Integration for Finance Operations"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or 'http://localhost:8002/api'
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_credit_note(self, data: Dict) -> Optional[Dict]:
        """
        Create credit note for refund
        
        Args:
            data: Credit note data including customer_id, amount, reason
            
        Returns:
            Credit note details or None
        """
        try:
            response = requests.post(
                f'{self.base_url}/finance/credit-notes',
                headers=self.headers,
                json=data,
                timeout=15
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"ERP API error: {e}")
            return None
    
    def get_credit_note_status(self, credit_note_id: str) -> Optional[Dict]:
        """Get credit note status"""
        try:
            response = requests.get(
                f'{self.base_url}/finance/credit-notes/{credit_note_id}',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"ERP API error: {e}")
            return None
    
    def process_refund(self, customer_account: str, amount: float, 
                      reference: str) -> Optional[Dict]:
        """
        Process refund to customer account
        
        Args:
            customer_account: Customer's KAPCI account ID
            amount: Refund amount
            reference: Ticket reference number
            
        Returns:
            Transaction details or None
        """
        try:
            response = requests.post(
                f'{self.base_url}/finance/refunds',
                headers=self.headers,
                json={
                    'customer_account': customer_account,
                    'amount': amount,
                    'reference': reference,
                    'type': 'compensation_refund'
                },
                timeout=15
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"ERP API error: {e}")
            return None
    
    def get_product_price(self, product_sku: str) -> Optional[float]:
        """Get product price from ERP"""
        try:
            response = requests.get(
                f'{self.base_url}/products/{product_sku}/price',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('price')
            return None
        except Exception as e:
            logger.error(f"ERP API error: {e}")
            return None


class InventoryService:
    """Inventory Management System Integration"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or 'http://localhost:8003/api'
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def check_stock(self, product_sku: str, quantity: int = 1) -> Dict:
        """
        Check product stock availability
        
        Args:
            product_sku: Product SKU
            quantity: Required quantity
            
        Returns:
            Stock status dict
        """
        try:
            response = requests.get(
                f'{self.base_url}/inventory/check',
                headers=self.headers,
                params={'sku': product_sku, 'qty': quantity},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return {'available': False, 'quantity': 0}
        except Exception as e:
            logger.error(f"Inventory API error: {e}")
            return {'available': False, 'quantity': 0}
    
    def reserve_stock(self, product_sku: str, quantity: int, 
                     reference: str) -> Optional[Dict]:
        """
        Reserve stock for replacement order
        
        Args:
            product_sku: Product SKU
            quantity: Quantity to reserve
            reference: Ticket reference
            
        Returns:
            Reservation details or None
        """
        try:
            response = requests.post(
                f'{self.base_url}/inventory/reserve',
                headers=self.headers,
                json={
                    'sku': product_sku,
                    'quantity': quantity,
                    'reference': reference,
                    'type': 'compensation_replacement'
                },
                timeout=10
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Inventory API error: {e}")
            return None
    
    def create_delivery_order(self, data: Dict) -> Optional[Dict]:
        """
        Create delivery order for replacement
        
        Args:
            data: Delivery order data
            
        Returns:
            Delivery order details with tracking
        """
        try:
            response = requests.post(
                f'{self.base_url}/delivery/orders',
                headers=self.headers,
                json=data,
                timeout=15
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Inventory API error: {e}")
            return None
    
    def get_delivery_status(self, tracking_number: str) -> Optional[Dict]:
        """Get delivery status by tracking number"""
        try:
            response = requests.get(
                f'{self.base_url}/delivery/track/{tracking_number}',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Inventory API error: {e}")
            return None
    
    def get_product_info(self, product_sku: str) -> Optional[Dict]:
        """Get product information"""
        try:
            response = requests.get(
                f'{self.base_url}/products/{product_sku}',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Inventory API error: {e}")
            return None


# Singleton instances (initialized with app config)
crm_service = CRMService()
erp_service = ERPService()
inventory_service = InventoryService()


def init_external_services(app):
    """Initialize external services with app configuration"""
    global crm_service, erp_service, inventory_service
    
    crm_service = CRMService(
        base_url=app.config.get('CRM_API_URL'),
        api_key=app.config.get('CRM_API_KEY')
    )
    
    erp_service = ERPService(
        base_url=app.config.get('ERP_API_URL'),
        api_key=app.config.get('ERP_API_KEY')
    )
    
    inventory_service = InventoryService(
        base_url=app.config.get('INVENTORY_API_URL'),
        api_key=app.config.get('INVENTORY_API_KEY')
    )
