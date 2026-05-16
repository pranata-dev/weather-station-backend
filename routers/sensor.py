from fastapi import APIRouter
from datetime import datetime, timezone
from models.sensor import SensorData

router = APIRouter()

@router.post("/data")
def ingest_sensor_data(data: SensorData):
    print(f"Received sensor data: MAC: {data.mac_address}, Temp: {data.temperature}, Humidity: {data.humidity}, Pressure: {data.pressure}")
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
