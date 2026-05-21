import sqlite3

DB_FILE = "weather_telemetry_v4.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_direction INTEGER,
                wind_speed REAL,
                solar_radiation REAL,
                uv_index INTEGER,
                rain REAL,
                pm1 REAL,
                pm2_5 REAL
            )
        """)
        conn.commit()
    finally:
        conn.close()

def insert_sensor_data(
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
                temperature, humidity, pressure, wind_direction, wind_speed,
                solar_radiation, uv_index, rain, pm1, pm2_5
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                temperature, humidity, pressure, wind_direction, wind_speed,
                solar_radiation, uv_index, rain, pm1, pm2_5
            )
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def get_latest_telemetry() -> dict | None:
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM weather_telemetry 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def get_telemetry_history(limit: int = 100) -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM (
                SELECT *
                FROM weather_telemetry 
                ORDER BY timestamp DESC 
                LIMIT ?
            )
            ORDER BY timestamp ASC
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

def update_latest_pm_data(pm1: float, pm2_5: float) -> bool:
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE weather_telemetry
            SET pm1 = ?, pm2_5 = ?
            WHERE id = (
                SELECT id FROM weather_telemetry
                ORDER BY timestamp DESC
                LIMIT 1
            )
            """,
            (pm1, pm2_5)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()
