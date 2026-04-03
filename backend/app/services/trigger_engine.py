import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import (
    Worker, Policy, Zone, City, DisruptionEvent, Claim
)
from app.models.schemas import (
    DisruptionEventCreate, DisruptionEventResponse
)
from app.services.external_data import ExternalDataService


TRIGGER_CONFIGS = {
    "heavy_rainfall": {"threshold": 64.5, "unit": "mm/24h", "source": "OpenWeatherMap/IMD"},
    "extreme_heat": {"threshold": 45.0, "unit": "°C", "source": "OpenWeatherMap/IMD"},
    "severe_aqi": {"threshold": 400.0, "unit": "AQI", "source": "CPCB AQI API"},
    "cyclone": {"threshold": 1, "unit": "red_alert", "source": "IMD Disaster alerts"},
    "curfew": {"threshold": 1, "unit": "official_notification", "source": "Government civic alert"},
    "strike": {"threshold": 1, "unit": "zone_closure", "source": "Civic alert mock"},
}


class TriggerEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.is_running = False
        self.external_data = ExternalDataService()

    async def start_monitoring(self):
        self.is_running = True
        while self.is_running:
            await self.check_all_triggers()
            await asyncio.sleep(300)

    async def stop_monitoring(self):
        self.is_running = False

    async def check_all_triggers(self):
        for trigger_type, config in TRIGGER_CONFIGS.items():
            await self._check_trigger(trigger_type, config)

    async def _check_trigger(self, trigger_type: str, config: Dict):
        data = await self._fetch_trigger_data(trigger_type)
        
        for zone_id, value in data.items():
            if self._exceeds_threshold(value, config["threshold"], trigger_type):
                await self._trigger_event(zone_id, trigger_type, value, config)

    async def _fetch_trigger_data(self, trigger_type: str) -> Dict[int, float]:
        zones_result = await self.db.execute(select(Zone))
        zones = zones_result.scalars().all()
        
        data = {}
        for zone in zones:
            triggers = await self.external_data.check_all_triggers_for_zone(zone)
            for trigger in triggers:
                if trigger["trigger_type"] == trigger_type:
                    data[zone.id] = trigger["value"]
                    break
        
        if not data:
            for zone in zones:
                if random.random() < 0.02:
                    if trigger_type == "heavy_rainfall":
                        data[zone.id] = random.uniform(65, 100)
                    elif trigger_type == "extreme_heat":
                        data[zone.id] = random.uniform(45, 48)
                    elif trigger_type == "severe_aqi":
                        data[zone.id] = random.uniform(400, 500)
                    elif trigger_type in ["cyclone", "curfew", "strike"]:
                        data[zone.id] = 1
        
        return data

    def _exceeds_threshold(self, value: float, threshold: float, trigger_type: str) -> bool:
        if trigger_type in ["cyclone", "curfew", "strike"]:
            return value >= threshold
        return value > threshold

    async def _trigger_event(self, zone_id: int, trigger_type: str, 
                           value: float, config: Dict):
        event_data = {
            "zone_id": zone_id,
            "trigger_type": trigger_type,
            "severity": self._determine_severity(value, trigger_type),
            "start_time": datetime.utcnow(),
            "data": {
                "value": value,
                "threshold": config["threshold"],
                "unit": config["unit"],
                "source": config["source"]
            },
            "is_verified": False
        }
        
        event = DisruptionEvent(**event_data)
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        await self.initiate_claims_for_event(event)

    def _determine_severity(self, value: float, trigger_type: str) -> str:
        if trigger_type == "heavy_rainfall":
            if value > 90: return "critical"
            if value > 75: return "high"
            return "medium"
        elif trigger_type == "extreme_heat":
            if value > 47: return "critical"
            return "high"
        elif trigger_type == "severe_aqi":
            if value > 450: return "critical"
            return "high"
        else:
            return "high"

    async def initiate_claims_for_event(self, event: DisruptionEvent):
        workers_result = await self.db.execute(
            select(Worker)
            .join(Policy)
            .where(
                Worker.primary_zone_id == event.zone_id,
                Worker.is_active == True,
                Policy.status == "active"
            )
        )
        workers = workers_result.scalars().all()
        
        for worker in workers:
            policy_result = await self.db.execute(
                select(Policy)
                .where(
                    Policy.worker_id == worker.id,
                    Policy.status == "active"
                )
            )
            policy = policy_result.scalar_one_or_none()
            
            if policy:
                amount = self._calculate_payout(policy, event)
                
                claim = Claim(
                    worker_id=worker.id,
                    policy_id=policy.id,
                    disruption_event_id=event.id,
                    amount=amount,
                    status="pending",
                    payout_status="pending"
                )
                self.db.add(claim)
        
        await self.db.commit()

    def _calculate_payout(self, policy: Policy, event: DisruptionEvent) -> float:
        if event.end_time:
            hours = (event.end_time - event.start_time).total_seconds() / 3600
        else:
            hours = 4
        
        avg_hourly = policy.weekly_premium * 2
        payout = avg_hourly * min(hours, policy.coverage_hours)
        
        return round(payout, 2)

    async def simulate_disruption(self, zone_id: int, trigger_type: str) -> DisruptionEvent:
        config = TRIGGER_CONFIGS.get(trigger_type)
        if not config:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        value = config["threshold"] + 10
        event = DisruptionEvent(
            zone_id=zone_id,
            trigger_type=trigger_type,
            severity="high",
            start_time=datetime.utcnow(),
            data={"value": value, "threshold": config["threshold"], "simulated": True},
            is_verified=True
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        await self.initiate_claims_for_event(event)
        
        return event

    async def get_active_events(self) -> List[DisruptionEvent]:
        result = await self.db.execute(
            select(DisruptionEvent)
            .where(DisruptionEvent.end_time == None)
            .order_by(DisruptionEvent.start_time.desc())
        )
        return list(result.scalars().all())

    async def get_zone_events(self, zone_id: int) -> List[DisruptionEvent]:
        result = await self.db.execute(
            select(DisruptionEvent)
            .where(DisruptionEvent.zone_id == zone_id)
            .order_by(DisruptionEvent.start_time.desc())
        )
        return list(result.scalars().all())
