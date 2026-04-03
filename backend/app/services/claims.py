import uuid
import random
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Claim, Worker
from app.models.schemas import ClaimUpdate
from app.services.notifications import whatsapp_service
from app.services.email import email_service


class PayoutService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_claim(self, claim_id: int) -> dict:
        result = await self.db.execute(
            select(Claim).where(Claim.id == claim_id)
        )
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise ValueError("Claim not found")
        
        if claim.status not in ["approved"]:
            raise ValueError(f"Cannot process claim with status: {claim.status}")
        
        if claim.fraud_confidence == "low":
            claim.status = "rejected"
            claim.payout_status = "rejected"
            await self.db.commit()
            return {"status": "rejected", "reason": "Low fraud confidence"}
        
        tx_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        claim.payout_status = "paid"
        claim.payout_transaction_id = tx_id
        await self.db.commit()
        
        await self._send_notifications(claim)
        
        return {
            "status": "paid",
            "transaction_id": tx_id,
            "amount": claim.amount,
            "worker_id": claim.worker_id
        }

    async def _send_notifications(self, claim: Claim):
        result = await self.db.execute(
            select(Worker).where(Worker.id == claim.worker_id)
        )
        worker = result.scalar_one_or_none()
        
        if worker:
            await whatsapp_service.send_claim_approved_notification(
                worker_phone=worker.phone,
                amount=claim.amount,
                claim_id=claim.id
            )
            
            email_service.send_claim_approved(
                email=f"{worker.phone}@gigshield.in",
                name=worker.name,
                claim_id=claim.id,
                amount=claim.amount
            )

    async def process_approved_claims(self) -> List[dict]:
        result = await self.db.execute(
            select(Claim).where(
                Claim.status == "approved",
                Claim.payout_status == "pending"
            )
        )
        claims = result.scalars().all()
        
        results = []
        for claim in claims:
            result = await self.process_claim(claim.id)
            results.append(result)
        
        return results

    async def get_worker_payout_history(self, worker_id: int) -> List[Claim]:
        result = await self.db.execute(
            select(Claim).where(
                Claim.worker_id == worker_id,
                Claim.payout_status == "paid"
            )
        )
        return list(result.scalars().all())


class ClaimsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payout_service = PayoutService(db)
        self.fraud_service = None

    def set_fraud_service(self, fraud_service):
        self.fraud_service = fraud_service

    async def get_claim(self, claim_id: int) -> Optional[Claim]:
        result = await self.db.execute(
            select(Claim).where(Claim.id == claim_id)
        )
        return result.scalar_one_or_none()

    async def get_all_claims(self, status: Optional[str] = None) -> List[Claim]:
        query = select(Claim)
        if status:
            query = query.where(Claim.status == status)
        result = await self.db.execute(query.order_by(Claim.created_at.desc()))
        return list(result.scalars().all())

    async def approve_claim(self, claim_id: int, review_notes: Optional[str] = None) -> Claim:
        claim = await self.get_claim(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        
        claim.status = "approved"
        claim.review_notes = review_notes
        await self.db.commit()
        await self.db.refresh(claim)
        
        await self.payout_service.process_claim(claim_id)
        
        return claim

    async def reject_claim(self, claim_id: int, review_notes: str) -> Claim:
        claim = await self.get_claim(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        
        claim.status = "rejected"
        claim.review_notes = review_notes
        claim.payout_status = "rejected"
        await self.db.commit()
        await self.db.refresh(claim)
        
        return claim

    async def update_claim_status(self, claim_id: int, update: ClaimUpdate) -> Claim:
        claim = await self.get_claim(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        
        if update.status:
            claim.status = update.status
        if update.fraud_score:
            claim.fraud_score = update.fraud_score
        if update.fraud_confidence:
            claim.fraud_confidence = update.fraud_confidence
        if update.payout_status:
            claim.payout_status = update.payout_status
        if update.payout_transaction_id:
            claim.payout_transaction_id = update.payout_transaction_id
        if update.review_notes:
            claim.review_notes = update.review_notes
        
        claim.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(claim)
        
        return claim

    async def auto_process_claim(self, claim_id: int) -> dict:
        claim = await self.get_claim(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        
        if self.fraud_service:
            fraud_result = await self.fraud_service.analyze_claim(claim_id)
            claim.fraud_score = fraud_result.fraud_score
            claim.fraud_confidence = fraud_result.confidence
            
            if fraud_result.confidence == "high":
                claim.status = "approved"
                await self.db.commit()
                payout_result = await self.payout_service.process_claim(claim_id)
                return {"status": "auto_approved", **payout_result}
            elif fraud_result.confidence == "medium":
                claim.status = "under_review"
                await self.db.commit()
                return {"status": "held_for_review", "claim_id": claim_id}
            else:
                claim.status = "under_review"
                await self.db.commit()
                return {"status": "manual_review_required", "claim_id": claim_id}
        
        return {"status": "no_fraud_service"}
