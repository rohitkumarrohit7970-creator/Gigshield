import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import (
    Worker, Policy, DisruptionEvent, Claim, Zone, 
    Earning
)
from app.models.schemas import (
    ClaimCreate, ClaimResponse, FraudScoreResponse
)


class FraudDetectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_claim(self, claim_id: int) -> FraudScoreResponse:
        result = await self.db.execute(
            select(Claim).where(Claim.id == claim_id)
        )
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise ValueError("Claim not found")
        
        worker_result = await self.db.execute(
            select(Worker).where(Worker.id == claim.worker_id)
        )
        worker = worker_result.scalar_one_or_none()
        
        event_result = await self.db.execute(
            select(DisruptionEvent).where(DisruptionEvent.id == claim.disruption_event_id)
        )
        event = event_result.scalar_one_or_none()
        
        signals = await self._gather_signals(worker, event)
        fraud_score = self._calculate_fraud_score(signals)
        confidence = self._get_confidence_level(fraud_score)
        
        claim.fraud_score = fraud_score
        claim.fraud_confidence = confidence
        await self.db.commit()
        
        return FraudScoreResponse(
            fraud_score=round(fraud_score, 3),
            confidence=confidence,
            signals=signals
        )

    async def _gather_signals(self, worker: Worker, event: DisruptionEvent) -> Dict:
        prior_activity = await self._get_prior_platform_activity(worker.id, event.start_time)
        gps_variance = self._simulate_gps_variance()
        cell_tower_match = random.random() > 0.2
        spatial_cluster = random.randint(1, 10)
        
        return {
            "prior_platform_activity": prior_activity,
            "gps_variance": gps_variance,
            "cell_tower_match": cell_tower_match,
            "spatial_cluster_count": spatial_cluster,
            "temporal_cluster_breadth": random.uniform(0.5, 4.0),
            "historical_claim_frequency": random.uniform(0.0, 0.3)
        }

    async def _get_prior_platform_activity(self, worker_id: int, before_time: datetime) -> float:
        cutoff = before_time - timedelta(hours=2)
        result = await self.db.execute(
            select(Earning).where(
                Earning.worker_id == worker_id,
                Earning.date >= cutoff,
                Earning.date < before_time
            )
        )
        earnings = result.scalars().all()
        
        if earnings:
            return sum(e.orders_completed for e in earnings) / len(earnings)
        return 0.0

    def _simulate_gps_variance(self) -> float:
        return random.uniform(0.001, 0.05)

    def _calculate_fraud_score(self, signals: Dict) -> float:
        score = 0.0
        
        if signals["prior_platform_activity"] < 0.5:
            score += 0.3
        elif signals["prior_platform_activity"] < 2.0:
            score += 0.15
        
        if signals["gps_variance"] < 0.005:
            score += 0.25
        
        if not signals["cell_tower_match"]:
            score += 0.15
        
        if signals["spatial_cluster_count"] > 5:
            score += 0.2
        
        if signals["temporal_cluster_breadth"] < 1.0:
            score += 0.15
        
        return min(score, 1.0)

    def _get_confidence_level(self, score: float) -> str:
        if score < 0.3:
            return "high"
        elif score < 0.6:
            return "medium"
        else:
            return "low"

    async def batch_analyze_claims(self, claim_ids: List[int]) -> List[FraudScoreResponse]:
        results = []
        for claim_id in claim_ids:
            result = await self.analyze_claim(claim_id)
            results.append(result)
        return results
