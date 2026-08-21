from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sensor, station
from database import init_db

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://weatherstationmonitoring.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensor.router, prefix="/api/v1/sensor")
app.include_router(station.router, prefix="/api/v1/stations")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "online", "message": "Weather Station API is running"}