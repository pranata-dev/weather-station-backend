from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- Wajib di-import
from routers import sensor
from database import init_db

init_db()

app = FastAPI()

# --- BLOK CORS (WAJIB DITAMBAHKAN) ---
# Ini yang ngasih izin ke localhost:3000 atau Vercel buat narik data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tanda "*" artinya mengizinkan dari semua URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------------------

app.include_router(sensor.router, prefix="/api/v1/sensor")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "online", "message": "Weather Station API is running"}