from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Worker, Earning, Policy
from app.models.schemas import WorkerResponse, WorkerDetailResponse, EarningResponse, PolicyResponse, WorkerUpdate
from app.core.security import get_current_user
from app.services.onboarding import OnboardingService

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("/me", response_model=WorkerDetailResponse)
async def get_current_worker(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Worker)
        .options(selectinload(Worker.city), selectinload(Worker.primary_zone))
        .where(Worker.id == current_user["user_id"])
    )
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return worker


@router.patch("/me", response_model=WorkerResponse)
async def update_current_worker(
    update: WorkerUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Worker).where(Worker.id == current_user["user_id"])
    )
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    if update.name is not None:
        worker.name = update.name
    if update.upi_id is not None:
        worker.upi_id = update.upi_id
    if update.city_id is not None:
        worker.city_id = update.city_id
    if update.primary_zone_id is not None:
        worker.primary_zone_id = update.primary_zone_id
    
    await db.commit()
    await db.refresh(worker)
    
    return worker


@router.get("/me/earnings")
async def get_my_earnings(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    return await service.get_worker_earnings_history(current_user["user_id"])


@router.get("/me/policy", response_model=PolicyResponse)
async def get_my_policy(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    policy = await service.get_worker_policy(current_user["user_id"])
    
    if not policy:
        raise HTTPException(status_code=404, detail="No active policy found")
    
    return policy


@router.get("/me/claims")
async def get_my_claims(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    return await service.get_worker_claims(current_user["user_id"])


@router.get("/cities")
async def get_cities(db: AsyncSession = Depends(get_db)):
    from app.db.models import City
    result = await db.execute(select(City))
    return result.scalars().all()


@router.get("/cities/{city_id}/zones")
async def get_city_zones(city_id: int, db: AsyncSession = Depends(get_db)):
    from app.db.models import Zone
    result = await db.execute(
        select(Zone).where(Zone.city_id == city_id)
    )
    return result.scalars().all()


@router.get("/disruptions/active")
async def get_active_disruptions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.db.models import DisruptionEvent
    worker_result = await db.execute(
        select(Worker).where(Worker.id == current_user["user_id"])
    )
    worker = worker_result.scalar_one_or_none()
    
    if not worker:
        return []
    
    result = await db.execute(
        select(DisruptionEvent)
        .where(DisruptionEvent.zone_id == worker.primary_zone_id)
        .where(DisruptionEvent.end_time == None)
        .order_by(DisruptionEvent.start_time.desc())
    )
    return result.scalars().all()
