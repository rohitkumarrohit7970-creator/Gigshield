from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models import Worker, Earning, Policy, Zone, City
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.schemas import (
    WorkerCreate, WorkerResponse, PremiumCalculationRequest, 
    PremiumCalculationResponse, PolicyCreate, PolicyResponse
)


class OnboardingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_worker(self, worker_data: WorkerCreate) -> Worker:
        result = await self.db.execute(
            select(Worker).where(Worker.phone == worker_data.phone)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Worker with this phone number already exists")
        
        worker = Worker(
            phone=worker_data.phone,
            name=worker_data.name,
            delivery_platform=worker_data.delivery_platform,
            platform_id=worker_data.platform_id,
            city_id=worker_data.city_id,
            primary_zone_id=worker_data.primary_zone_id,
            hashed_password=get_password_hash(worker_data.password),
            upi_id=worker_data.upi_id,
            role=worker_data.role or "worker",
            is_active=True
        )
        self.db.add(worker)
        await self.db.commit()
        await self.db.refresh(worker)
        return worker

    async def authenticate_worker(self, phone: str, password: str) -> Optional[Worker]:
        result = await self.db.execute(
            select(Worker).where(Worker.phone == phone)
        )
        worker = result.scalar_one_or_none()
        if not worker or not verify_password(password, worker.hashed_password):
            return None
        return worker

    async def create_auth_token(self, worker: Worker) -> dict:
        token = create_access_token(
            data={"sub": str(worker.id), "role": worker.role or "worker"},
            expires_delta=timedelta(weeks=1)
        )
        return {"access_token": token, "token_type": "bearer", "role": worker.role or "worker"}

    async def get_worker_earnings_history(self, worker_id: int) -> dict:
        result = await self.db.execute(
            select(Earning).where(Earning.worker_id == worker_id)
        )
        earnings = result.scalars().all()
        
        if not earnings:
            return {"avg_daily": 0, "avg_hourly": 0, "total_days": 0}
        
        total_amount = sum(e.amount for e in earnings)
        total_hours = sum(e.hours_worked for e in earnings)
        total_days = len(set(e.date.date() for e in earnings))
        
        return {
            "avg_daily": total_amount / max(total_days, 1),
            "avg_hourly": total_hours / max(sum(e.hours_worked for e in earnings), 1),
            "total_days": total_days,
            "total_earnings": total_amount
        }

    async def calculate_premium(self, request: PremiumCalculationResponse) -> PremiumCalculationResponse:
        city_result = await self.db.execute(
            select(City).where(City.id == request.city_id)
        )
        city = city_result.scalar_one_or_none()
        
        zone_result = await self.db.execute(
            select(Zone).where(Zone.id == request.zone_id)
        )
        zone = zone_result.scalar_one_or_none()
        
        if not city or not zone:
            raise ValueError("Invalid city or zone")
        
        base_premium = request.avg_daily_income * 0.05
        
        city_risk_factor = city.risk_multiplier
        zone_risk_factor = 1 + zone.risk_score
        coverage_factor = request.coverage_hours / 8
        
        final_premium = base_premium * city_risk_factor * zone_risk_factor * coverage_factor
        
        return PremiumCalculationResponse(
            weekly_premium=round(final_premium, 2),
            base_premium=round(base_premium, 2),
            city_risk_factor=round(city_risk_factor, 2),
            zone_risk_factor=round(zone_risk_factor, 2),
            coverage_factor=round(coverage_factor, 2)
        )

    async def create_policy(self, worker_id: int, zone_id: int, 
                           coverage_hours: int, weekly_premium: float) -> Policy:
        coverage_start = self._get_next_monday()
        
        policy = Policy(
            worker_id=worker_id,
            zone_id=zone_id,
            coverage_hours=coverage_hours,
            weekly_premium=weekly_premium,
            status="active",
            coverage_start_date=coverage_start,
            coverage_end_date=None
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    def _get_next_monday(self) -> datetime:
        today = datetime.utcnow()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        return today + timedelta(days=days_until_monday)

    async def get_worker_policy(self, worker_id: int) -> Optional[Policy]:
        result = await self.db.execute(
            select(Policy)
            .where(Policy.worker_id == worker_id)
            .where(Policy.status == "active")
            .order_by(Policy.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_worker_claims(self, worker_id: int) -> List[Policy]:
        from app.db.models import Claim
        result = await self.db.execute(
            select(Claim).where(Claim.worker_id == worker_id)
        )
        return list(result.scalars().all())
