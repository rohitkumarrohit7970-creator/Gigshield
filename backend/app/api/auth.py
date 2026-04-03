from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import LoginRequest, Token, WorkerCreate, WorkerResponse, PremiumCalculationRequest, PremiumCalculationResponse, PolicyResponse
from app.services.onboarding import OnboardingService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=WorkerResponse)
async def register(
    worker_data: WorkerCreate,
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    try:
        worker = await service.register_worker(worker_data)
        return worker
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingService(db)
    worker = await service.authenticate_worker(login_data.phone, login_data.password)
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    return await service.create_auth_token(worker)


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
