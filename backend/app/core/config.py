from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "GigShield"
    APP_VERSION: str = "1.0.0"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/gigshield"
    
    SECRET_KEY: str = "gigshield-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 7
    
    OPENWEATHERMAP_API_KEY: Optional[str] = None
    CPCB_AQI_API_URL: str = "https://api.cpcb.gov.in/api/v1/aqi"
    
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
