from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Worker, Policy, Claim
from app.models.schemas import StatsResponse, DisruptionEventResponse, ClaimDetailResponse, ClaimResponse
from app.services.trigger_engine import TriggerEngine
from app.core.security import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    total_workers = await db.scalar(select(func.count(Worker.id)))
    active_policies = await db.scalar(
        select(func.count(Policy.id)).where(Policy.status == "active")
    )
    total_claims = await db.scalar(select(func.count(Claim.id)))
    approved_claims = await db.scalar(
        select(func.count(Claim.id)).where(Claim.status == "approved")
    )
    pending_claims = await db.scalar(
        select(func.count(Claim.id)).where(Claim.status == "pending")
    )
    
    total_payouts = await db.scalar(
        select(func.sum(Claim.amount)).where(Claim.payout_status == "paid")
    ) or 0
    
    loss_ratio = (total_payouts / (active_policies * 50)) if active_policies else 0
    
    return StatsResponse(
        total_workers=total_workers or 0,
        active_policies=active_policies or 0,
        total_claims=total_claims or 0,
        approved_claims=approved_claims or 0,
        pending_claims=pending_claims or 0,
        total_payouts=round(total_payouts, 2),
        loss_ratio=round(loss_ratio, 3)
    )


@router.get("/disruptions/active", response_model=list[DisruptionEventResponse])
async def get_active_disruptions(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    engine = TriggerEngine(db)
    return await engine.get_active_events()


@router.post("/disruptions/simulate")
async def simulate_disruption(
    zone_id: int,
    trigger_type: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    engine = TriggerEngine(db)
    try:
        event = await engine.simulate_disruption(zone_id, trigger_type)
        return {"status": "success", "event_id": event.id}
    except ValueError as e:
        return {"status": "error", "detail": str(e)}


@router.get("/claims/pending", response_model=list[ClaimResponse])
async def get_pending_claims(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Claim)
        .options(selectinload(Claim.worker), selectinload(Claim.policy), selectinload(Claim.disruption_event))
        .where(Claim.status.in_(["pending", "under_review"]))
    )
    return result.scalars().all()


@router.get("/claims/review-queue", response_model=list[ClaimResponse])
async def get_review_queue(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Claim)
        .options(selectinload(Claim.worker), selectinload(Claim.policy), selectinload(Claim.disruption_event))
        .where(Claim.fraud_confidence == "medium")
    )
    return result.scalars().all()
