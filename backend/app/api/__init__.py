from fastapi import APIRouter
from app.api import auth, workers, policies, claims, admin, payments

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(workers.router)
api_router.include_router(policies.router)
api_router.include_router(claims.router)
api_router.include_router(admin.router)
api_router.include_router(payments.router)
