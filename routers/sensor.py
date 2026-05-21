from fastapi import APIRouter, Request, HTTPException
import datetime
from database import insert_sensor_data, get_latest_telemetry, get_telemetry_history, update_latest_pm_data

router = APIRouter()

def fahrenheit_to_celsius(f: float) -> float:
    return round((f - 32.0) * 5.0 / 9.0, 2)

@router.post("/data")
async def receive_sensor_data(request: Request):
    try:
        latest = get_latest_telemetry()
        if latest and "timestamp" in latest:
            try:
                latest_time = datetime.datetime.strptime(latest["timestamp"], "%Y-%m-%d %H:%M:%S")
                latest_time = latest_time.replace(tzinfo=datetime.timezone.utc)
                current_time = datetime.datetime.now(datetime.timezone.utc)
                
                diff = (current_time - latest_time).total_seconds()
                if diff < 300:
                    return {"status": "skipped", "message": "Throttled"}
            except Exception as e:
                print(f"Throttle time parsing error: {e}")

        form_data = await request.form()
        
        temp_f = float(form_data.get("tempf", 0.0))
        temperature = fahrenheit_to_celsius(temp_f)
        
        humidity = float(form_data.get("humidity", 0.0))
        
        baromrelin = float(form_data.get("baromrelin", 0.0))
        pressure = round(baromrelin * 33.8639, 2)
        
        wind_direction = int(float(form_data.get("winddir", 0)))
        
        windspeedmph = float(form_data.get("windspeedmph", 0.0))
        wind_speed = round(windspeedmph * 1.60934, 2)
        
        solar_radiation = float(form_data.get("solarradiation", 0.0))
        
        uv_index = int(float(form_data.get("uv", 0)))
        
        dailyrainin = float(form_data.get("dailyrainin", 0.0))
        rain = round(dailyrainin * 25.4, 2)
        
        pm1 = float(form_data.get("pm1_ch1", form_data.get("pm1", 0.0)))
        pm2_5 = float(form_data.get("pm25_ch1", form_data.get("pm25", 0.0)))

        insert_sensor_data(
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            wind_direction=wind_direction,
            wind_speed=wind_speed,
            solar_radiation=solar_radiation,
            uv_index=uv_index,
            rain=rain,
            pm1=pm1,
            pm2_5=pm2_5
        )

        print("Successfully inserted 10 telemetry parameters.")
        return {"status": "success"}

    except Exception as e:
        print(f"Error parsing data: {e}")
        return {"status": "error parsing, but connection OK"}

@router.get("/latest")
async def get_latest():
    data = get_latest_telemetry()
    if data is None:
        raise HTTPException(status_code=404, detail="No telemetry data found")
    return {"status": "success", "data": data}

@router.get("/history")
async def get_history(limit: int = 100):
    data = get_telemetry_history(limit)
    return {"status": "success", "data": data}

@router.post("/pm")
async def receive_pm_data(request: Request):
    try:
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            payload = await request.json()
        else:
            payload = dict(await request.form())
        
        pm1 = float(payload.get("pm1", 0.0))
        pm2_5 = float(payload.get("pm2_5", payload.get("pm25", 0.0)))
        
        # Tangkap lat dan lon dari payload ESP32
        lat = payload.get("lat")
        lon = payload.get("lon")
        
        # Konversi ke float jika tidak None
        if lat is not None and lon is not None:
            lat = float(lat)
            lon = float(lon)

        updated = update_latest_pm_data(pm1=pm1, pm2_5=pm2_5, lat=lat, lon=lon)

        if updated:
            print(f"PM data merged: PM1={pm1}, PM2.5={pm2_5}, Lat={lat}, Lon={lon}")
            return {"status": "success"}
        else:
            print("PM update failed: no existing telemetry row found.")
            return {"status": "error", "message": "No telemetry row to update"}

    except Exception as e:
        print(f"Error parsing PM data: {e}")
        return {"status": "error", "message": str(e)}