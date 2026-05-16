from pydantic import BaseModel

class SensorData(BaseModel):
    mac_address: str
    temperature: float
    humidity: float
    pressure: float
