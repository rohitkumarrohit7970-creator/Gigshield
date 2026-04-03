import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@gigshield.in")
        self.from_name = os.getenv("FROM_NAME", "GigShield")
        self.use_mock = not self.smtp_host or not self.smtp_user
    
    def _send_email(self, to_email: str, subject: str, body: str, html: Optional[str] = None) -> Dict:
        if self.use_mock:
            return {
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "timestamp": datetime.utcnow().isoformat(),
                "test_mode": True
            }
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return {
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "failed",
                "to": to_email,
                "error": str(e),
                "test_mode": True
            }
    
    def send_claim_approved(self, email: str, name: str, claim_id: int, amount: float) -> Dict:
        subject = f"🎉 Claim Approved - #{claim_id}"
        body = f"""
Dear {name},

Your claim #{claim_id} has been approved!

Amount: ₹{amount:.2f}
Status: Payment Initiated

You will receive the payout within 24 hours to your registered UPI ID.

Thank you for being a part of GigShield!

Best regards,
GigShield Team
        """
        return self._send_email(email, subject, body)
    
    def send_claim_rejected(self, email: str, name: str, claim_id: int, reason: str) -> Dict:
        subject = f"Claim Update - #{claim_id}"
        body = f"""
Dear {name},

Your claim #{claim_id} has been reviewed.

Status: Not Approved
Reason: {reason}

If you believe this is an error, please contact our support team.

Best regards,
GigShield Team
        """
        return self._send_email(email, subject, body)
    
    def send_payment_receipt(self, email: str, name: str, amount: float, policy_id: int) -> Dict:
        subject = f"Payment Receipt - Policy #{policy_id}"
        body = f"""
Dear {name},

We have received your payment.

Amount: ₹{amount:.2f}
Policy ID: #{policy_id}
Status: Active

Your coverage is now active!

Best regards,
GigShield Team
        """
        return self._send_email(email, subject, body)
    
    def send_policy_expiry_reminder(self, email: str, name: str, days_left: int, policy_id: int) -> Dict:
        subject = f"Policy Expiry Reminder - {days_left} days left"
        body = f"""
Dear {name},

Your GigShield policy (#{policy_id}) expires in {days_left} days.

Please renew your policy to continue enjoying income protection benefits.

Renew now at: https://gigshield.in

Best regards,
GigShield Team
        """
        return self._send_email(email, subject, body)
    
    def send_disruption_alert(self, email: str, name: str, zone_name: str, trigger_type: str) -> Dict:
        trigger_messages = {
            "heavy_rainfall": "heavy rainfall",
            "extreme_heat": "extreme heat conditions",
            "severe_aqi": "poor air quality",
            "cyclone": "cyclone warning",
            "curfew": "curfew in your area"
        }
        
        trigger_name = trigger_messages.get(trigger_type, trigger_type)
        
        subject = f"🚨 Disruption Alert - {zone_name}"
        body = f"""
Dear {name},

We have detected a disruption in your area: {trigger_name}

An automatic claim may be generated if you have active coverage.

Check your dashboard for details: https://gigshield.in/dashboard

Stay safe!

Best regards,
GigShield Team
        """
        return self._send_email(email, subject, body)


email_service = EmailService()