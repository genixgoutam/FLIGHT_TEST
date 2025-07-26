from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from backend.database import get_db
from backend.models import Airport, AirTraffic
from backend.schemas import (
    Airport as AirportSchema, 
    AirportCreate, 
    AirportSearchRequest, 
    AirportSearchResponse,
    SystemStats,
    AirTraffic as AirTrafficSchema
)

router = APIRouter()

@router.get("/airports")
async def get_airports(
    skip: int = 0,
    limit: int = 10000,  # Show ALL airports (no practical limit)
    db: Session = Depends(get_db)
):
    """Get all airports - Django equivalent of api_airports"""
    airports = db.query(Airport).offset(skip).limit(limit).all()

    # Convert to frontend-compatible format
    airport_list = []
    for airport in airports:
        airport_list.append({
            "id": airport.id,
            "code": airport.code,
            "name": airport.name,
            "latitude": airport.latitude,
            "longitude": airport.longitude,
            "country": airport.country or "",
            "city": airport.city or "",
            "type": airport.type or "unknown"
        })

    return airport_list

@router.get("/airports/find/{code}")
async def find_airport_by_code(code: str, db: Session = Depends(get_db)):
    """Find a specific airport by code"""
    airport = db.query(Airport).filter(
        (Airport.code == code.upper()) |
        (Airport.iata_code == code.upper()) |
        (Airport.icao_code == code.upper())
    ).first()

    if airport:
        return {
            "found": True,
            "airport": {
                "id": airport.id,
                "code": airport.code,
                "name": airport.name,
                "latitude": airport.latitude,
                "longitude": airport.longitude,
                "country": airport.country or "",
                "city": airport.city or "",
                "type": airport.type or "unknown",
                "iata_code": airport.iata_code or "",
                "icao_code": airport.icao_code or ""
            }
        }
    else:
        return {"found": False, "message": f"Airport with code '{code}' not found"}

@router.get("/airports/stats")
async def get_airport_stats(db: Session = Depends(get_db)):
    """Get airport statistics"""
    total_airports = db.query(Airport).count()

    # Get sample of airport codes
    sample_airports = db.query(Airport.code, Airport.name).limit(20).all()

    return {
        "total_airports": total_airports,
        "sample_codes": [{"code": a.code, "name": a.name} for a in sample_airports],
        "message": f"Database contains {total_airports} airports"
    }

@router.get("/airports/{airport_id}", response_model=AirportSchema)
async def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Get specific airport by ID"""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if airport is None:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

@router.post("/airports", response_model=AirportSchema)
async def create_airport(airport: AirportCreate, db: Session = Depends(get_db)):
    """Create new airport"""
    db_airport = Airport(**airport.dict())
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    return db_airport

@router.get("/all_airports")
async def get_all_airports_with_location(db: Session = Depends(get_db)):
    """Get airports with location data - Django equivalent of api_all_airports"""
    airports = db.query(Airport).all()
    
    data = {
        'airports': []
    }
    
    for airport in airports:
        data['airports'].append({
            'id': airport.id,
            'name': airport.name,
            'code': airport.code,
            'latitude': airport.latitude,
            'longitude': airport.longitude,
            'type': airport.type or 'domestic',
            'city': airport.city or '',
            'country': airport.country or ''
        })
    
    return data

@router.get("/stops")
async def get_stops(db: Session = Depends(get_db)):
    """Get airport stops - Django equivalent of api_stops"""
    airports = db.query(Airport).all()
    
    stops = []
    for airport in airports:
        stops.append({
            'code': airport.code,
            'name': airport.name,
            'latitude': airport.latitude,
            'longitude': airport.longitude,
            'country': airport.country or ''
        })
    
    return {'stops': stops}

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics - Django equivalent of api_stats"""
    total_airports = db.query(Airport).count()
    total_countries = db.query(Airport.country).distinct().count()
    
    # Import here to avoid circular imports
    from backend.models import Route, OptimizationResult
    total_routes = db.query(Route).count()
    optimization_runs = db.query(OptimizationResult).count()
    
    return SystemStats(
        total_airports=total_airports,
        total_countries=total_countries,
        total_routes=total_routes,
        optimization_runs=optimization_runs
    )

@router.get("/countries")
async def get_countries(db: Session = Depends(get_db)):
    """Get list of countries - Django equivalent of api_countries"""
    countries = db.query(Airport.country).distinct().all()
    countries = [c[0] for c in countries if c[0]]  # Filter out None/empty values
    return countries

@router.get("/airports/search")
async def search_airports_get(
    q: str = "",
    page: int = 1,
    country: str = "",
    type: str = "",
    db: Session = Depends(get_db)
):
    """Search airports via GET - Frontend compatible"""
    query = db.query(Airport)

    # Apply filters
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (Airport.name.ilike(search_term)) |
            (Airport.code.ilike(search_term)) |
            (Airport.city.ilike(search_term))
        )

    if country:
        query = query.filter(Airport.country.ilike(f"%{country}%"))

    if type:
        query = query.filter(Airport.type.ilike(f"%{type}%"))

    # Pagination
    per_page = 10
    total_count = query.count()
    total_pages = math.ceil(total_count / per_page)

    start = (page - 1) * per_page
    airports = query.offset(start).limit(per_page).all()

    # Convert to dict format
    results = []
    for airport in airports:
        results.append({
            "id": airport.id,
            "code": airport.code,
            "name": airport.name,
            "latitude": airport.latitude,
            "longitude": airport.longitude,
            "country": airport.country,
            "city": airport.city,
            "type": airport.type
        })

    return {
        "results": results,
        "count": total_count,
        "total_pages": total_pages,
        "current_page": page
    }

@router.post("/airports/search", response_model=AirportSearchResponse)
async def search_airports_post(
    search_request: AirportSearchRequest,
    db: Session = Depends(get_db)
):
    """Search airports via POST - API compatible"""
    return await search_airports_get(
        q=search_request.q or "",
        page=search_request.page or 1,
        country=search_request.country or "",
        type=search_request.type or "",
        db=db
    )

@router.get("/air_traffic")
async def get_air_traffic(db: Session = Depends(get_db)):
    """Get air traffic data - Django equivalent of api_air_traffic"""
    # Get active air traffic
    air_traffic = db.query(AirTraffic).filter(AirTraffic.is_active == True).limit(20).all()
    
    # If no real data, generate mock data
    if not air_traffic:
        import random
        mock_traffic = []
        for i in range(10):
            mock_traffic.append({
                'callsign': f'FL{1000 + i}',
                'latitude': random.uniform(-90, 90),
                'longitude': random.uniform(-180, 180),
                'altitude': random.randint(25000, 45000),
                'speed': random.randint(400, 600)
            })
        return {'air_traffic': mock_traffic}
    
    # Convert to response format
    traffic_data = []
    for traffic in air_traffic:
        traffic_data.append({
            'callsign': traffic.callsign,
            'latitude': traffic.latitude,
            'longitude': traffic.longitude,
            'altitude': traffic.altitude,
            'speed': traffic.speed
        })
    
    return {'air_traffic': traffic_data}

@router.post("/air_traffic", response_model=AirTrafficSchema)
async def create_air_traffic(
    callsign: str,
    latitude: float,
    longitude: float,
    altitude: int,
    speed: int,
    heading: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Create new air traffic entry"""
    air_traffic = AirTraffic(
        callsign=callsign,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        speed=speed,
        heading=heading
    )
    
    db.add(air_traffic)
    db.commit()
    db.refresh(air_traffic)
    
    return air_traffic
