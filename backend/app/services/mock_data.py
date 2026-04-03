import random
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import (
    City, Zone, Worker, Earning, Policy, Payment, 
    DisruptionEvent, Claim
)
from app.core.security import get_password_hash


CITIES_DATA = [
    {"name": "Mumbai", "tier": 1, "risk_multiplier": 1.2},
    {"name": "Delhi", "tier": 1, "risk_multiplier": 1.3},
    {"name": "Bengaluru", "tier": 1, "risk_multiplier": 1.0},
    {"name": "Hyderabad", "tier": 1, "risk_multiplier": 0.9},
    {"name": "Chennai", "tier": 1, "risk_multiplier": 1.1},
]

ZONES_DATA = {
    "Mumbai": [
        {"name": "Andheri West", "lat": 19.1361, "lng": 72.8278, "disruption_rate": 0.15, "risk_score": 0.6},
        {"name": "Bandra West", "lat": 19.0544, "lng": 72.8403, "disruption_rate": 0.12, "risk_score": 0.5},
        {"name": "Powai", "lat": 19.1131, "lng": 72.9250, "disruption_rate": 0.08, "risk_score": 0.4},
        {"name": "Dharavi", "lat": 19.0438, "lng": 72.8539, "disruption_rate": 0.20, "risk_score": 0.7},
        {"name": "Churchgate", "lat": 18.9355, "lng": 72.8273, "disruption_rate": 0.10, "risk_score": 0.45},
    ],
    "Delhi": [
        {"name": "Connaught Place", "lat": 28.6318, "lng": 77.2197, "disruption_rate": 0.18, "risk_score": 0.65},
        {"name": "Saket", "lat": 28.5244, "lng": 77.2050, "disruption_rate": 0.14, "risk_score": 0.55},
        {"name": "Dwarka", "lat": 28.5921, "lng": 77.0375, "disruption_rate": 0.16, "risk_score": 0.6},
        {"name": "Rohini", "lat": 28.7408, "lng": 77.3249, "disruption_rate": 0.11, "risk_score": 0.5},
        {"name": "Karol Bagh", "lat": 28.6518, "lng": 77.1893, "disruption_rate": 0.22, "risk_score": 0.75},
    ],
    "Bengaluru": [
        {"name": "Koramangala", "lat": 12.9352, "lng": 77.6245, "disruption_rate": 0.09, "risk_score": 0.4},
        {"name": "MG Road", "lat": 12.9752, "lng": 77.6060, "disruption_rate": 0.07, "risk_score": 0.35},
        {"name": "Whitefield", "lat": 13.0105, "lng": 77.7566, "disruption_rate": 0.13, "risk_score": 0.55},
        {"name": "Indiranagar", "lat": 12.9789, "lng": 77.6407, "disruption_rate": 0.08, "risk_score": 0.4},
        {"name": "JP Nagar", "lat": 12.9166, "lng": 77.5850, "disruption_rate": 0.11, "risk_score": 0.5},
    ],
    "Hyderabad": [
        {"name": "Gachibowli", "lat": 17.4401, "lng": 78.3527, "disruption_rate": 0.10, "risk_score": 0.45},
        {"name": "Jubilee Hills", "lat": 17.4307, "lng": 78.4090, "disruption_rate": 0.06, "risk_score": 0.35},
        {"name": "Banjara Hills", "lat": 17.4224, "lng": 78.4404, "disruption_rate": 0.08, "risk_score": 0.4},
        {"name": "Madhapur", "lat": 17.4485, "lng": 78.3908, "disruption_rate": 0.12, "risk_score": 0.5},
        {"name": "Ameerpet", "lat": 17.4131, "lng": 78.4423, "disruption_rate": 0.14, "risk_score": 0.55},
    ],
    "Chennai": [
        {"name": "T Nagar", "lat": 13.0524, "lng": 80.2460, "disruption_rate": 0.15, "risk_score": 0.6},
        {"name": "Anna Nagar", "lat": 13.0839, "lng": 80.2099, "disruption_rate": 0.11, "risk_score": 0.5},
        {"name": "Adyar", "lat": 13.0013, "lng": 80.2564, "disruption_rate": 0.13, "risk_score": 0.55},
        {"name": "Porur", "lat": 13.0415, "lng": 80.1567, "disruption_rate": 0.09, "risk_score": 0.45},
        {"name": "OMR", "lat": 12.9180, "lng": 80.2292, "disruption_rate": 0.07, "risk_score": 0.4},
    ],
}

PLATFORM_NAMES = ["Zomato", "Swiggy"]
WORKER_NAMES = [
    "Rajesh Kumar", "Amit Singh", "Priya Sharma", "Vikram Patel", "Anita Reddy",
    "Sanjay Gupta", "Meera Nair", "Arjun Menon", "Kavita Das", "Rajiv Joshi",
    "Sunita Devi", "Mohammad Khan", "Lakshmi Iyer", "Bharat Sharma", "Divya Singh",
    "Gopal Krishna", "Reshma Begum", "Suresh Choudhury", "Pooja Mukherjee", "Arun Venkatesh"
]


async def seed_cities(db: AsyncSession) -> List[City]:
    result = await db.execute(select(City))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    cities = []
    for city_data in CITIES_DATA:
        city = City(**city_data)
        db.add(city)
        cities.append(city)
    await db.commit()
    return cities


async def seed_zones(db: AsyncSession, cities: List[City]) -> List[Zone]:
    result = await db.execute(select(Zone))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    zones = []
    for city in cities:
        city_zones = ZONES_DATA.get(city.name, [])
        for z in city_zones:
            zone = Zone(
                name=z["name"],
                city_id=city.id,
                latitude=z["lat"],
                longitude=z["lng"],
                disruption_rate_12m=z["disruption_rate"],
                risk_score=z["risk_score"]
            )
            db.add(zone)
            zones.append(zone)
    await db.commit()
    return zones


async def seed_workers(db: AsyncSession, cities: List[City], zones: List[Zone]) -> List[Worker]:
    result = await db.execute(select(Worker))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    workers = []
    workers_by_city = {city.id: [z for z in zones if z.city_id == city.id] for city in cities}
    
    admin = Worker(
        phone="+919999999999",
        name="Admin",
        delivery_platform="Admin",
        platform_id="ADMIN001",
        city_id=cities[0].id,
        primary_zone_id=zones[0].id,
        hashed_password=get_password_hash("admin123"),
        upi_id="admin@gigshield",
        role="admin",
        is_active=True
    )
    db.add(admin)
    workers.append(admin)
    
    for i in range(50):
        city = random.choice(cities)
        city_zones = workers_by_city[city.id]
        zone = random.choice(city_zones)
        
        worker = Worker(
            phone=f"+919{random.randint(100000000, 999999999)}",
            name=random.choice(WORKER_NAMES) if i < len(WORKER_NAMES) else f"Worker {i+1}",
            delivery_platform=random.choice(PLATFORM_NAMES),
            platform_id=f"PLT{random.randint(10000, 99999)}",
            city_id=city.id,
            primary_zone_id=zone.id,
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(worker)
        workers.append(worker)
    
    await db.commit()
    return workers


async def seed_earnings(db: AsyncSession, workers: List[Worker]) -> List[Earning]:
    result = await db.execute(select(Earning))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    earnings = []
    for worker in workers:
        for days_ago in range(28):
            date = datetime.utcnow() - timedelta(days=days_ago)
            daily_amount = random.uniform(600, 1200)
            hours = random.uniform(6, 10)
            orders = int(hours * random.uniform(3, 6))
            
            earning = Earning(
                worker_id=worker.id,
                date=date,
                amount=daily_amount,
                hours_worked=hours,
                orders_completed=orders
            )
            db.add(earning)
            earnings.append(earning)
    
    await db.commit()
    return earnings


async def seed_policies(db: AsyncSession, workers: List[Worker], zones: List[Zone]) -> List[Policy]:
    result = await db.execute(select(Policy))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    policies = []
    coverage_options = [6, 8, 10]
    
    for worker in workers[:40]:
        coverage_hours = random.choice(coverage_options)
        avg_daily = random.uniform(600, 1200)
        base_premium = avg_daily * 0.05
        zone_risk = worker.primary_zone_id
        zone = next(z for z in zones if z.id == zone_risk)
        premium = base_premium * (1 + zone.risk_score)
        
        coverage_start = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        policy = Policy(
            worker_id=worker.id,
            zone_id=worker.primary_zone_id,
            coverage_hours=coverage_hours,
            weekly_premium=round(premium, 2),
            status="active",
            coverage_start_date=coverage_start,
            coverage_end_date=None
        )
        db.add(policy)
        policies.append(policy)
    
    await db.commit()
    return policies


async def seed_disruption_events(db: AsyncSession, zones: List[Zone]) -> List[DisruptionEvent]:
    result = await db.execute(select(DisruptionEvent))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    events = []
    trigger_types = ["heavy_rainfall", "extreme_heat", "severe_aqi", "cyclone", "curfew", "strike"]
    severities = ["low", "medium", "high", "critical"]
    
    for zone in zones[:15]:
        if random.random() < 0.3:
            trigger = random.choice(trigger_types)
            severity = random.choice(severities)
            start = datetime.utcnow() - timedelta(days=random.randint(1, 60))
            end = start + timedelta(hours=random.randint(2, 12))
            
            event = DisruptionEvent(
                zone_id=zone.id,
                trigger_type=trigger,
                severity=severity,
                start_time=start,
                end_time=end,
                data={"source": "mock", "threshold_breached": True},
                is_verified=True
            )
            db.add(event)
            events.append(event)
    
    await db.commit()
    return events


async def seed_claims(db: AsyncSession, workers: List[Worker], policies: List[Policy], 
                       events: List[DisruptionEvent]) -> List[Claim]:
    result = await db.execute(select(Claim))
    existing = result.scalars().all()
    if existing:
        return list(existing)
    
    claims = []
    statuses = ["pending", "approved", "rejected", "under_review"]
    
    for policy in policies[:20]:
        if random.random() < 0.4 and events:
            worker = next(w for w in workers if w.id == policy.worker_id)
            event = random.choice(events)
            amount = random.uniform(100, 500)
            status = random.choice(statuses)
            
            claim = Claim(
                worker_id=worker.id,
                policy_id=policy.id,
                disruption_event_id=event.id,
                amount=amount,
                status=status,
                fraud_score=random.uniform(0.1, 0.9) if status != "pending" else None,
                fraud_confidence="low" if status == "pending" else random.choice(["high", "medium", "low"]),
                payout_status="paid" if status == "approved" else "pending"
            )
            db.add(claim)
            claims.append(claim)
    
    await db.commit()
    return claims


async def seed_all(db: AsyncSession):
    print("Seeding cities...")
    cities = await seed_cities(db)
    
    print("Seeding zones...")
    zones = await seed_zones(db, cities)
    
    print("Seeding workers...")
    workers = await seed_workers(db, cities, zones)
    
    print("Seeding earnings...")
    await seed_earnings(db, workers)
    
    print("Seeding policies...")
    policies = await seed_policies(db, workers, zones)
    
    print("Seeding disruption events...")
    events = await seed_disruption_events(db, zones)
    
    print("Seeding claims...")
    await seed_claims(db, workers, policies, events)
    
    print("Database seeding complete!")
