import os
import razorpay
from typing import Optional, Dict, Any
from datetime import datetime


class PaymentService:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID", "test_key_id"), os.getenv("RAZORPAY_KEY_SECRET", "test_key_secret"))
        )
        self.test_mode = os.getenv("RAZORPAY_TEST_MODE", "true").lower() == "true"
    
    def create_order(self, amount: float, currency: str = "INR", receipt: Optional[str] = None) -> Dict[str, Any]:
        if self.test_mode:
            return {
                "id": f"order_test_{datetime.utcnow().timestamp()}",
                "amount": int(amount * 100),
                "currency": currency,
                "status": "created",
                "receipt": receipt or f"receipt_{datetime.utcnow().timestamp()}",
                "test_mode": True
            }
        
        order_data = {
            "amount": int(amount * 100),
            "currency": currency,
            "receipt": receipt or f"receipt_{datetime.utcnow().timestamp()}",
            "payment_capture": 1
        }
        
        return self.client.order.create(order_data)
    
    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        if self.test_mode:
            return True
        
        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
            return True
        except:
            return False
    
    def create_payout(self, worker_upi: str, amount: float, claim_id: int) -> Dict[str, Any]:
        if self.test_mode:
            return {
                "id": f"payout_test_{claim_id}",
                "status": "credited",
                "amount": amount,
                "worker_upi": worker_upi,
                "claim_id": claim_id,
                "timestamp": datetime.utcnow().isoformat(),
                "test_mode": True,
                "message": "Test payout processed successfully"
            }
        
        return {
            "id": f"payout_{datetime.utcnow().timestamp()}",
            "status": "processing",
            "amount": amount,
            "worker_upi": worker_upi,
            "claim_id": claim_id
        }
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        if self.test_mode:
            return {
                "id": payment_id,
                "status": "captured",
                "test_mode": True
            }
        
        return self.client.payment.fetch(payment_id)


class SubscriptionService:
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service
    
    def create_weekly_subscription(self, worker_id: int, premium_amount: float) -> Dict[str, Any]:
        return {
            "subscription_id": f"sub_{worker_id}_{datetime.utcnow().timestamp()}",
            "worker_id": worker_id,
            "amount": premium_amount,
            "frequency": "weekly",
            "status": "active",
            "next_billing_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "test_mode": self.payment_service.test_mode
        }
    
    def process_weekly_payment(self, subscription_id: str) -> Dict[str, Any]:
        if self.payment_service.test_mode:
            return {
                "status": "success",
                "subscription_id": subscription_id,
                "timestamp": datetime.utcnow().isoformat(),
                "test_mode": True
            }
        return {"status": "pending", "subscription_id": subscription_id}


from datetime import timedelta