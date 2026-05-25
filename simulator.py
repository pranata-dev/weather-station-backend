import requests
import time
import random
from datetime import datetime, timezone

url = "http://localhost:8000/api/v1/sensor/data"

while True:
    payload = {
        "PASSKEY": "A4:CF:12:8B:3E:04",
        "stationtype": "Ecowitt_Simulator",
        "dateutc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "tempf": round(random.uniform(80.0, 95.0), 2),
        "humidity": random.randint(55, 85),
        "baromrelin": round(random.uniform(29.70, 30.10), 2)
    }
    
    try:
        response = requests.post(url, data=payload)
        status_code = response.status_code
    except requests.RequestException as e:
        status_code = f"Error: {e}"

    print(f"Sent payload: {payload}")
    print(f"Status Code: {status_code}")
    print("-" * 50)
    
    time.sleep(5)