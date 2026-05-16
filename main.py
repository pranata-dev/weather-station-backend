from fastapi import FastAPI
from routers import sensor

app = FastAPI()

app.include_router(sensor.router, prefix="/api/v1/sensor")

@app.get("/health")
def health_check():
    return {"status": "ok"}
