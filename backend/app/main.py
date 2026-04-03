from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db, AsyncSessionLocal
from app.api import api_router
from app.services.mock_data import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    async with AsyncSessionLocal() as db:
        await seed_all(db)
    
    yield


app = FastAPI(
    title="GigShield API",
    description="""
## GigShield - Parametric Insurance for Gig Workers

### Features
- **Worker Management** - Register, login, profile management
- **Policy Management** - Create, view, and manage insurance policies
- **Claims Processing** - Automated and manual claim processing
- **Disruption Monitoring** - Real-time weather and event monitoring
- **Analytics** - Admin dashboard with statistics

### Authentication
All endpoints (except login/register) require Bearer token authentication.

### Demo Credentials
- **Admin**: +919999999999 / admin123
- **Worker**: +919708159742 / password123
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "GigShield API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
