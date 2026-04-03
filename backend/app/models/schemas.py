from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CityBase(BaseModel):
    name: str
    tier: int
    risk_multiplier: float = 1.0


class CityResponse(CityBase):
    id: int

    class Config:
        from_attributes = True


class ZoneBase(BaseModel):
    name: str
    city_id: int
    latitude: float
    longitude: float
    disruption_rate_12m: float = 0.0
    risk_score: float = 0.5


class ZoneResponse(ZoneBase):
    id: int

    class Config:
        from_attributes = True


class WorkerCreate(BaseModel):
    phone: str
    name: str
    delivery_platform: str
    platform_id: str
    city_id: int
    primary_zone_id: int
    password: str
    upi_id: Optional[str] = None
    role: Optional[str] = "worker"


class WorkerResponse(BaseModel):
    id: int
    phone: str
    name: str
    delivery_platform: str
    platform_id: str
    city_id: int
    primary_zone_id: int
    upi_id: Optional[str] = None
    role: str = "worker"
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    upi_id: Optional[str] = None
    city_id: Optional[int] = None
    primary_zone_id: Optional[int] = None


class WorkerDetailResponse(WorkerResponse):
    city: CityResponse
    primary_zone: ZoneResponse


class EarningBase(BaseModel):
    worker_id: int
    date: datetime
    amount: float
    hours_worked: float
    orders_completed: int = 0


class EarningResponse(EarningBase):
    id: int

    class Config:
        from_attributes = True


class PolicyCreate(BaseModel):
    worker_id: int
    zone_id: int
    coverage_hours: int = Field(ge=6, le=10)
    weekly_premium: float


class PolicyResponse(BaseModel):
    id: int
    worker_id: int
    zone_id: int
    coverage_hours: int
    weekly_premium: float
    status: str
    coverage_start_date: datetime
    coverage_end_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyDetailResponse(PolicyResponse):
    zone: ZoneResponse


class PaymentCreate(BaseModel):
    policy_id: int
    amount: float
    payment_method: str = "upi"


class PaymentResponse(PaymentCreate):
    id: int
    status: str
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DisruptionEventCreate(BaseModel):
    zone_id: int
    trigger_type: str
    severity: str
    start_time: datetime
    end_time: Optional[datetime] = None
    data: Optional[dict] = None
    is_verified: bool = False


class DisruptionEventResponse(DisruptionEventCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClaimCreate(BaseModel):
    worker_id: int
    policy_id: int
    disruption_event_id: int
    amount: float


class ClaimUpdate(BaseModel):
    status: Optional[str] = None
    fraud_score: Optional[float] = None
    fraud_confidence: Optional[str] = None
    payout_status: Optional[str] = None
    payout_transaction_id: Optional[str] = None
    reviewed_by: Optional[int] = None
    review_notes: Optional[str] = None


class ClaimResponse(ClaimCreate):
    id: int
    status: str
    fraud_score: Optional[float]
    fraud_confidence: Optional[str]
    payout_status: str
    payout_transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClaimDetailResponse(ClaimResponse):
    worker: WorkerResponse
    policy: PolicyResponse
    disruption_event: DisruptionEventResponse


class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = "worker"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: str = "worker"


class LoginRequest(BaseModel):
    phone: str
    password: str


class PremiumCalculationRequest(BaseModel):
    city_id: int
    zone_id: int
    avg_daily_income: float
    coverage_hours: int = Field(ge=6, le=10)


class PremiumCalculationResponse(BaseModel):
    weekly_premium: float
    base_premium: float
    city_risk_factor: float
    zone_risk_factor: float
    coverage_factor: float


class FraudScoreResponse(BaseModel):
    fraud_score: float
    confidence: str
    signals: dict


class TriggerConfig(BaseModel):
    trigger_type: str
    threshold: float
    unit: str


class StatsResponse(BaseModel):
    total_workers: int
    active_policies: int
    total_claims: int
    approved_claims: int
    pending_claims: int
    total_payouts: float
    loss_ratio: float


class PaymentOrderRequest(BaseModel):
    amount: float
    policy_id: int
    payment_type: str = "premium"


class PaymentOrderResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    status: str
    receipt: Optional[str]


class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentVerificationResponse(BaseModel):
    verified: bool
    message: str


class PayoutRequest(BaseModel):
    worker_upi: str
    amount: float
    claim_id: int


class PayoutResponse(BaseModel):
    payout_id: str
    status: str
    amount: float
    message: str
