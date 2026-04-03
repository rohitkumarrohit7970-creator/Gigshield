from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import (
    PaymentOrderRequest, PaymentOrderResponse,
    PaymentVerificationRequest, PaymentVerificationResponse,
    PayoutRequest, PayoutResponse
)
from app.services.payment import PaymentService
from app.core.security import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])
payment_service = PaymentService()


@router.post("/create-order", response_model=PaymentOrderResponse)
async def create_payment_order(
    request: PaymentOrderRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    receipt = f"premium_{request.policy_id}_{current_user.get('user_id')}"
    order = payment_service.create_order(
        amount=request.amount,
        receipt=receipt
    )
    return PaymentOrderResponse(**order)


@router.post("/verify", response_model=PaymentVerificationResponse)
async def verify_payment(
    request: PaymentVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    verified = payment_service.verify_payment_signature(
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature
    )
    return PaymentVerificationResponse(
        verified=verified,
        message="Payment verified successfully" if verified else "Payment verification failed"
    )


@router.post("/payout", response_model=PayoutResponse)
async def create_payout(
    request: PayoutRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can process payouts")
    
    result = payment_service.create_payout(
        worker_upi=request.worker_upi,
        amount=request.amount,
        claim_id=request.claim_id
    )
    return PayoutResponse(
        payout_id=result["id"],
        status=result.get("status", "completed"),
        amount=result["amount"],
        message=result.get("message", "Payout processed")
    )


@router.get("/status/{payment_id}")
async def get_payment_status(payment_id: str):
    status = payment_service.get_payment_status(payment_id)
    return status