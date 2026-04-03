from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.models.schemas import ClaimResponse, ClaimUpdate
from app.core.security import get_current_user
from app.services.claims import ClaimsService

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get("", response_model=list[ClaimResponse])
async def get_all_claims(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ClaimsService(db)
    return await service.get_all_claims(status)


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ClaimsService(db)
    claim = await service.get_claim(claim_id)
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return claim


@router.post("/{claim_id}/approve")
async def approve_claim(
    claim_id: int,
    review_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ClaimsService(db)
    try:
        claim = await service.approve_claim(claim_id, review_notes)
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{claim_id}/reject")
async def reject_claim(
    claim_id: int,
    review_notes: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ClaimsService(db)
    try:
        claim = await service.reject_claim(claim_id, review_notes)
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{claim_id}")
async def update_claim(
    claim_id: int,
    update: ClaimUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ClaimsService(db)
    try:
        claim = await service.update_claim_status(claim_id, update)
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{claim_id}/auto-process")
async def auto_process_claim(
    claim_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.services.fraud_detection import FraudDetectionService
    
    service = ClaimsService(db)
    fraud_service = FraudDetectionService(db)
    service.set_fraud_service(fraud_service)
    
    try:
        result = await service.auto_process_claim(claim_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
