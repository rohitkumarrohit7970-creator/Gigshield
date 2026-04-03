import os
import httpx
from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Zone


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.use_mock = not self.api_key or self.api_key == "demo"
    
    async def get_weather_data(self, lat: float, lon: float) -> Dict:
        if self.use_mock:
            return self._get_mock_weather(lat, lon)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "rain_24h": data.get("rain", {}).get("1h", 0),
                        "description": data["weather"][0]["description"],
                        "source": "OpenWeatherMap"
                    }
            except Exception as e:
                print(f"Weather API error: {e}")
        
        return self._get_mock_weather(lat, lon)
    
    def _get_mock_weather(self, lat: float, lon: float) -> Dict:
        import random
        return {
            "temperature": random.uniform(20, 40),
            "humidity": random.uniform(40, 90),
            "rain_24h": random.uniform(0, 50) if random.random() < 0.1 else 0,
            "description": "clear sky",
            "source": "mock"
        }
    
    async def check_rainfall_trigger(self, zone: Zone) -> Optional[Dict]:
        weather = await self.get_weather_data(zone.latitude, zone.longitude)
        
        if weather["rain_24h"] > 64.5:
            return {
                "trigger_type": "heavy_rainfall",
                "value": weather["rain_24h"],
                "threshold": 64.5,
                "unit": "mm/24h",
                "severity": "critical" if weather["rain_24h"] > 90 else "high",
                "source": weather["source"]
            }
        return None
    
    async def check_heat_trigger(self, zone: Zone) -> Optional[Dict]:
        weather = await self.get_weather_data(zone.latitude, zone.longitude)
        
        if weather["temperature"] > 45:
            return {
                "trigger_type": "extreme_heat",
                "value": weather["temperature"],
                "threshold": 45,
                "unit": "°C",
                "severity": "critical" if weather["temperature"] > 47 else "high",
                "source": weather["source"]
            }
        return None


class AQIAPIService:
    def __init__(self):
        self.api_key = os.getenv("CPCB_API_KEY", "")
        self.use_mock = not self.api_key or self.api_key == "demo"
    
    async def get_aqi_data(self, lat: float, lon: float) -> Dict:
        if self.use_mock:
            return self._get_mock_aqi(lat, lon)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.waqi.info/feed",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "token": self.api_key
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        return {
                            "aqi": data["data"]["aqi"],
                            "pollutant": data["data"]["dominantpollutant"],
                            "source": "WAQI"
                        }
            except Exception as e:
                print(f"AQI API error: {e}")
        
        return self._get_mock_aqi(lat, lon)
    
    def _get_mock_aqi(self, lat: float, lon: float) -> Dict:
        import random
        return {
            "aqi": random.uniform(50, 350),
            "pollutant": "pm25",
            "source": "mock"
        }
    
    async def check_aqi_trigger(self, zone: Zone) -> Optional[Dict]:
        aqi_data = await self.get_aqi_data(zone.latitude, zone.longitude)
        
        if aqi_data["aqi"] > 400:
            return {
                "trigger_type": "severe_aqi",
                "value": aqi_data["aqi"],
                "threshold": 400,
                "unit": "AQI",
                "severity": "critical" if aqi_data["aqi"] > 450 else "high",
                "pollutant": aqi_data["pollutant"],
                "source": aqi_data["source"]
            }
        return None


class IMDAlertsService:
    def __init__(self):
        self.api_key = os.getenv("IMD_API_KEY", "")
        self.use_mock = not self.api_key or self.api_key == "demo"
    
    async def check_cyclone_alert(self, zone: Zone) -> Optional[Dict]:
        if self.use_mock:
            import random
            if random.random() < 0.02:
                return {
                    "trigger_type": "cyclone",
                    "value": 1,
                    "threshold": 1,
                    "severity": "critical",
                    "source": "mock"
                }
            return None
        
        return None
    
    async def check_curfew_alert(self, zone: Zone, city_name: str) -> Optional[Dict]:
        import random
        if random.random() < 0.01:
            return {
                "trigger_type": "curfew",
                "value": 1,
                "threshold": 1,
                "severity": "high",
                "city": city_name,
                "source": "mock"
            }
        return None


class ExternalDataService:
    def __init__(self):
        self.weather_service = WeatherAPIService()
        self.aqi_service = AQIAPIService()
        self.imd_service = IMDAlertsService()
    
    async def check_all_triggers_for_zone(self, zone: Zone, city_name: str = "") -> List[Dict]:
        triggers = []
        
        rainfall = await self.weather_service.check_rainfall_trigger(zone)
        if rainfall:
            triggers.append(rainfall)
        
        heat = await self.weather_service.check_heat_trigger(zone)
        if heat:
            triggers.append(heat)
        
        aqi = await self.aqi_service.check_aqi_trigger(zone)
        if aqi:
            triggers.append(aqi)
        
        cyclone = await self.imd_service.check_cyclone_alert(zone)
        if cyclone:
            triggers.append(cyclone)
        
        curfew = await self.imd_service.check_curfew_alert(zone, city_name)
        if curfew:
            triggers.append(curfew)
        
        return triggers
    
    async def get_zone_weather_summary(self, zone: Zone) -> Dict:
        weather = await self.weather_service.get_weather_data(zone.latitude, zone.longitude)
        aqi = await self.aqi_service.get_aqi_data(zone.latitude, zone.longitude)
        
        return {
            "zone_id": zone.id,
            "zone_name": zone.name,
            "weather": weather,
            "aqi": aqi,
            "timestamp": datetime.utcnow().isoformat()
        }