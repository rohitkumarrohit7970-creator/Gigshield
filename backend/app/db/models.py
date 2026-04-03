from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    tier = Column(Integer, nullable=False)
    risk_multiplier = Column(Float, default=1.0)

    zones = relationship("Zone", back_populates="city")
    workers = relationship("Worker", back_populates="city")


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    disruption_rate_12m = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.5)

    city = relationship("City", back_populates="zones")
    workers = relationship("Worker", back_populates="primary_zone")
    disruption_events = relationship("DisruptionEvent", back_populates="zone")
    policies = relationship("Policy", back_populates="zone")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    delivery_platform = Column(String(50), nullable=False)
    platform_id = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    primary_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    upi_id = Column(String(100), nullable=True)
    role = Column(String(20), default="worker")  # worker or admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    city = relationship("City", back_populates="workers")
    primary_zone = relationship("Zone", back_populates="workers")
    policies = relationship("Policy", back_populates="worker")
    claims = relationship("Claim", back_populates="worker", foreign_keys="Claim.worker_id")
    earnings = relationship("Earning", back_populates="worker")


class Earning(Base):
    __tablename__ = "earnings"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    hours_worked = Column(Float, nullable=False)
    orders_completed = Column(Integer, default=0)

    worker = relationship("Worker", back_populates="earnings")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    coverage_hours = Column(Integer, nullable=False)
    weekly_premium = Column(Float, nullable=False)
    status = Column(String(20), default="active")
    coverage_start_date = Column(DateTime, nullable=False)
    coverage_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship("Worker", back_populates="policies")
    zone = relationship("Zone", back_populates="policies")
    payments = relationship("Payment", back_populates="policy")
    claims = relationship("Claim", back_populates="policy")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    payment_method = Column(String(50), default="upi")
    transaction_id = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    policy = relationship("Policy", back_populates="payments")


class DisruptionEvent(Base):
    __tablename__ = "disruption_events"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    trigger_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    zone = relationship("Zone", back_populates="disruption_events")
    claims = relationship("Claim", back_populates="disruption_event")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    disruption_event_id = Column(Integer, ForeignKey("disruption_events.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    fraud_score = Column(Float, nullable=True)
    fraud_confidence = Column(String(20), nullable=True)
    payout_status = Column(String(20), default="pending")
    payout_transaction_id = Column(String(100), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("workers.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    worker = relationship("Worker", back_populates="claims", foreign_keys=[worker_id])
    policy = relationship("Policy", back_populates="claims")
    disruption_event = relationship("DisruptionEvent", back_populates="claims")
