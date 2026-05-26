from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import hashlib
from database import register_station, list_stations_with_latest, update_station_details

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

class StationUpdate(BaseModel):
    name: str
    location: str

@router.put("/update/{station_code}")
async def update_station(station_code: str, update_data: StationUpdate):
    success = update_station_details(station_code, update_data.name, update_data.location)
    if success:
        return {"status": "success", "message": "Station updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Station not found or update failed")
