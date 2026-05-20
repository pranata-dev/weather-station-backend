from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/data")
async def receive_sensor_data(request: Request):
    # 1. Ambil data mentah berbentuk Form-Data dari alat
    form_data = await request.form()
    
    # 2. PAKSA CETAK ke terminal biar lo bisa liat isinya
    print("\n=== DATA MENTAH DARI ALAT AWS ===")
    for key, value in form_data.items():
        print(f"{key}: {value}")
    print("=================================\n")
    
    # Return 200 OK formalitas dulu biar alat gak mutus koneksi
    return {"status": "success"}