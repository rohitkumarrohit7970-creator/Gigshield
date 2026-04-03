import random
import numpy as np
from typing import Dict, List, Optional
from sklearn.ensemble import GradientBoostingRegressor
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import City, Zone, Worker, Earning, Policy
from app.models.schemas import PremiumCalculationRequest, PremiumCalculationResponse


class PremiumModel:
    def __init__(self):
        self.model = None
        self._train_model()

    def _train_model(self):
        X_train = []
        y_train = []
        
        for _ in range(500):
            city_risk = random.uniform(0.8, 1.5)
            zone_risk = random.uniform(0.3, 0.9)
            avg_income = random.uniform(600, 1200)
            coverage_hours = random.choice([6, 8, 10])
            
            features = [city_risk, zone_risk, avg_income, coverage_hours]
            base = avg_income * 0.05
            premium = base * city_risk * (1 + zone_risk) * (coverage_hours / 8)
            
            X_train.append(features)
            y_train.append(premium)
        
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            random_state=42
        )
        self.model.fit(X_train, y_train)

    async def calculate_premium(self, db: AsyncSession, 
                                 request: PremiumCalculationRequest) -> PremiumCalculationResponse:
        city_result = await db.execute(select(City).where(City.id == request.city_id))
        city = city_result.scalar_one_or_none()
        
        zone_result = await db.execute(select(Zone).where(Zone.id == request.zone_id))
        zone = zone_result.scalar_one_or_none()
        
        if not city or not zone:
            raise ValueError("Invalid city or zone")
        
        features = [
            city.risk_multiplier,
            zone.risk_score,
            request.avg_daily_income,
            request.coverage_hours
        ]
        
        predicted_premium = self.model.predict([features])[0]
        
        base_premium = request.avg_daily_income * 0.05
        
        return PremiumCalculationResponse(
            weekly_premium=round(max(predicted_premium, 20), 2),
            base_premium=round(base_premium, 2),
            city_risk_factor=round(city.risk_multiplier, 2),
            zone_risk_factor=round(1 + zone.risk_score, 2),
            coverage_factor=round(request.coverage_hours / 8, 2)
        )

    def get_model_info(self) -> Dict:
        return {
            "model_type": "GradientBoostingRegressor",
            "n_estimators": 100,
            "features": ["city_risk", "zone_risk", "avg_daily_income", "coverage_hours"],
            "training_samples": 500
        }


class TrendPredictionService:
    def __init__(self):
        self.historical_data = self._generate_historical_data()

    def _generate_historical_data(self) -> Dict:
        cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai"]
        data = {}
        
        for city in cities:
            dates = []
            values = []
            base_date = datetime.utcnow() - timedelta(days=90)
            
            for i in range(90):
                date = base_date + timedelta(days=i)
                value = random.uniform(0.05, 0.25)
                if random.random() < 0.1:
                    value += random.uniform(0.1, 0.2)
                
                dates.append(date)
                values.append(value)
            
            data[city] = {"dates": dates, "values": values}
        
        return data

    async def predict_disruption_probability(self, zone_id: int, 
                                              db: AsyncSession) -> Dict:
        zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
        zone = zone_result.scalar_one_or_none()
        
        if not zone:
            raise ValueError("Zone not found")
        
        city_result = await db.execute(select(City).where(City.id == zone.city_id))
        city = city_result.scalar_one_or_none()
        
        historical = self.historical_data.get(city.name, {}).get("values", [])
        
        if historical:
            recent = historical[-14:]
            avg_prob = np.mean(recent)
            std_prob = np.std(recent)
            prediction = avg_prob + random.uniform(-std_prob, std_prob)
        else:
            prediction = random.uniform(0.1, 0.2)
        
        return {
            "zone_id": zone_id,
            "zone_name": zone.name,
            "city_name": city.name,
            "disruption_probability": round(prediction, 3),
            "confidence": "medium",
            "prediction_period": "next_7_days",
            "factors": [
                "seasonal_pattern",
                "historical_disruption_rate",
                "weather_forecast"
            ]
        }

    async def get_zone_trends(self, zone_id: int, days: int = 30) -> Dict:
        zone_result = await self.db.execute(select(Zone).where(Zone.id == zone_id)) if hasattr(self, 'db') else None
        
        return {
            "zone_id": zone_id,
            "historical_claims": random.randint(0, 10),
            "predicted_claims": random.randint(1, 5),
            "trend": random.choice(["increasing", "stable", "decreasing"])
        }
