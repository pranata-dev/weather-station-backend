from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
from database import register_station, list_stations_with_latest

router = APIRouter()

class StationRegistration(BaseModel):
    station_code: str
    name: str
    api_key: str
    location: str
    access_password: str

@router.post("/register")
async def register(station: StationRegistration):
    success = register_station(
        station_code=station.station_code,
        name=station.name,
        api_key=station.api_key,
        location=station.location,
        access_password=station.access_password
    )
    
    if success:
        return {"status": "success", "message": "Station registered", "api_key": station.api_key}
    else:
        raise HTTPException(status_code=400, detail="Failed to register station. MAC or Code might already exist.")

@router.get("/list")
async def list_all_stations():
    stations = list_stations_with_latest()
    return {"status": "success", "data": stations}
