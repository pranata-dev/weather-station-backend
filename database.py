import sqlite3

DB_FILE = "weather_telemetry_v5.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_code TEXT UNIQUE,
                name TEXT,
                mac_address TEXT UNIQUE,
                api_key TEXT UNIQUE,
                location TEXT,
                access_password TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                api_key TEXT,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_direction INTEGER,
                wind_speed REAL,
                solar_radiation REAL,
                uv_index INTEGER,
                rain REAL,
                pm1 REAL,
                pm2_5 REAL,
                lat REAL,
                lon REAL,
                FOREIGN KEY(api_key) REFERENCES stations(api_key)
            )
        """)
        conn.commit()
    finally:
        conn.close()

def get_station_by_api_key(api_key: str) -> dict | None:
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stations WHERE api_key = ?", (api_key,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def register_station(station_code: str, name: str, mac_address: str, api_key: str, location: str, access_password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO stations (station_code, name, mac_address, api_key, location, access_password)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (station_code, name, mac_address, api_key, location, access_password)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def list_stations() -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, station_code, name, mac_address, api_key, location, created_at FROM stations")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def insert_sensor_data(
    api_key: str,
    temperature: float,
    humidity: float,
    pressure: float,
    wind_direction: int,
    wind_speed: float,
    solar_radiation: float,
    uv_index: int,
    rain: float,
    pm1: float,
    pm2_5: float
):
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO weather_telemetry (
                api_key, temperature, humidity, pressure, wind_direction, wind_speed,
                solar_radiation, uv_index, rain, pm1, pm2_5
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                api_key, temperature, humidity, pressure, wind_direction, wind_speed,
                solar_radiation, uv_index, rain, pm1, pm2_5
            )
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_latest_telemetry(api_key: str = None) -> dict | None:
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if api_key:
            cursor.execute("SELECT * FROM weather_telemetry WHERE api_key = ? ORDER BY timestamp DESC LIMIT 1", (api_key,))
        else:
            cursor.execute("SELECT * FROM weather_telemetry ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def get_telemetry_history(limit: int = 100, api_key: str = None) -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if api_key:
            cursor.execute(
                """
                SELECT * FROM (
                    SELECT * FROM weather_telemetry WHERE api_key = ? ORDER BY timestamp DESC LIMIT ?
                ) ORDER BY timestamp ASC
                """,
                (api_key, limit)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM (
                    SELECT * FROM weather_telemetry ORDER BY timestamp DESC LIMIT ?
                ) ORDER BY timestamp ASC
                """,
                (limit,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def update_latest_pm_data(pm1: float, pm2_5: float, api_key: str, lat: float = None, lon: float = None) -> bool:
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        if lat is not None and lon is not None:
            cursor.execute(
                """
                UPDATE weather_telemetry
                SET pm1 = ?, pm2_5 = ?, lat = ?, lon = ?
                WHERE id = (
                    SELECT id FROM weather_telemetry WHERE api_key = ? ORDER BY timestamp DESC LIMIT 1
                )
                """,
                (pm1, pm2_5, lat, lon, api_key)
            )
        else:
            cursor.execute(
                """
                UPDATE weather_telemetry
                SET pm1 = ?, pm2_5 = ?
                WHERE id = (
                    SELECT id FROM weather_telemetry WHERE api_key = ? ORDER BY timestamp DESC LIMIT 1
                )
                """,
                (pm1, pm2_5, api_key)
            )
            
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()