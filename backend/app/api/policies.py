from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import PolicyCreate, PolicyResponse, PremiumCalculationRequest, PremiumCalculationResponse
from app.core.security import get_current_user
from app.services.onboarding import OnboardingService

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.post("/create", response_model=PolicyResponse)
async def create_policy(
    policy_data: PolicyCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    policy = await service.create_policy(
        worker_id=current_user["user_id"],
        zone_id=policy_data.zone_id,
        coverage_hours=policy_data.coverage_hours,
        weekly_premium=policy_data.weekly_premium
    )
    return policy


@router.post("/premium", response_model=PremiumCalculationResponse)
async def calculate_premium(
    request: PremiumCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    try:
        return await service.calculate_premium(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
