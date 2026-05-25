from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
from database import register_station, list_stations

router = APIRouter()

class StationRegistration(BaseModel):
    station_code: str
    name: str
    mac_address: str
    location: str
    access_password: str

@router.post("/register")
async def register(station: StationRegistration):
    # Strip colons, uppercase, and hash to generate api_key
    clean_mac = station.mac_address.replace(":", "").upper()
    api_key = hashlib.md5(clean_mac.encode()).hexdigest()
    
    success = register_station(
        station_code=station.station_code,
        name=station.name,
        mac_address=station.mac_address,
        api_key=api_key,
        location=station.location,
        access_password=station.access_password
    )
    
    if success:
        return {"status": "success", "message": "Station registered", "api_key": api_key}
    else:
        raise HTTPException(status_code=400, detail="Failed to register station. MAC or Code might already exist.")

@router.get("/list")
async def list_all_stations():
    stations = list_stations()
    return {"status": "success", "data": stations}
