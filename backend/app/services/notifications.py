import os
import httpx
from typing import Optional, List, Dict
from datetime import datetime


class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.use_mock = not self.account_sid or not self.auth_token
    
    async def send_whatsapp_message(self, to: str, message: str) -> Dict:
        if self.use_mock:
            return {
                "sid": f"mock_msg_{datetime.utcnow().timestamp()}",
                "status": "sent",
                "to": to,
                "body": message,
                "test_mode": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    auth=(self.account_sid, self.auth_token),
                    data={
                        "From": self.from_number,
                        "To": to,
                        "Body": message
                    },
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        "sid": data.get("sid"),
                        "status": data.get("status"),
                        "to": data.get("to"),
                        "body": data.get("body"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except Exception as e:
                print(f"WhatsApp API error: {e}")
        
        return {
            "sid": f"mock_msg_{datetime.utcnow().timestamp()}",
            "status": "failed",
            "to": to,
            "error": str(e),
            "test_mode": True
        }
    
    async def send_claim_approved_notification(self, worker_phone: str, amount: float, claim_id: int) -> Dict:
        message = (
            f"🎉 GigShield: Your claim #{claim_id} has been approved!\n\n"
            f"Amount: ₹{amount:.2f}\n"
            f"Status: Payment initiated\n\n"
            f"You'll receive the payout within 24 hours."
        )
        return await self.send_whatsapp_message(f"whatsapp:{worker_phone}", message)
    
    async def send_claim_rejected_notification(self, worker_phone: str, claim_id: int, reason: str) -> Dict:
        message = (
            f"⚠️ GigShield: Your claim #{claim_id} was reviewed.\n\n"
            f"Status: Not Approved\n"
            f"Reason: {reason}\n\n"
            f"Contact support if you have questions."
        )
        return await self.send_whatsapp_message(f"whatsapp:{worker_phone}", message)
    
    async def send_disruption_alert(self, worker_phone: str, trigger_type: str, zone_name: str) -> Dict:
        trigger_messages = {
            "heavy_rainfall": "heavy rainfall",
            "extreme_heat": "extreme heat",
            "severe_aqi": "poor air quality",
            "cyclone": "cyclone warning",
            "curfew": "curfew in effect"
        }
        
        trigger_name = trigger_messages.get(trigger_type, trigger_type)
        
        message = (
            f"🚨 GigShield Alert\n\n"
            f"Disruption detected in {zone_name}: {trigger_name}.\n\n"
            f"A claim may be automatically generated for you if you have active coverage.\n"
            f"Check your dashboard for details."
        )
        return await self.send_whatsapp_message(f"whatsapp:{worker_phone}", message)
    
    async def send_payment_receipt(self, worker_phone: str, amount: float, policy_id: int) -> Dict:
        message = (
            f"✅ GigShield Payment Received\n\n"
            f"Policy ID: #{policy_id}\n"
            f"Amount: ₹{amount:.2f}\n"
            f"Status: Active\n\n"
            f"Your coverage is now active!"
        )
        return await self.send_whatsapp_message(f"whatsapp:{worker_phone}", message)
    
    async def send_coverage_expiry_reminder(self, worker_phone: str, days_left: int) -> Dict:
        message = (
            f"⏰ GigShield Reminder\n\n"
            f"Your coverage expires in {days_left} days.\n"
            f"Renew now to continue protection."
        )
        return await self.send_whatsapp_message(f"whatsapp:{worker_phone}", message)


whatsapp_service = WhatsAppService()