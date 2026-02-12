from flask import Flask, jsonify, request
import datetime
import requests

app = Flask(__name__)

SPOTS = {
    "carcavelos": {"name": "Carcavelos", "lat": 38.680, "lon": -9.336},
    "nazare": {"name": "Nazaré", "lat": 39.602, "lon": -9.070},
    "ericeira": {"name": "Ericeira", "lat": 38.962, "lon": -9.417},
}

def pick_spot(spot_key: str):
    if not spot_key:
        return SPOTS["carcavelos"]
    return SPOTS.get(spot_key.lower())

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "surf-data-service"})

@app.get("/data")
def data():
    return jsonify({
        "service": "surf-data-service",
        "message": "endpoint antigo /data (mantido)",
        "utc": datetime.datetime.utcnow().isoformat()
    })

@app.get("/forecast")
def forecast():
    spot_key = request.args.get("spot", "carcavelos")
    spot = pick_spot(spot_key)

    if not spot:
        return jsonify({
            "error": "spot desconhecido",
            "available_spots": list(SPOTS.keys())
        }), 400

    lat = spot["lat"]
    lon = spot["lon"]

    #API pública sem chave:
    marine_url = "https://marine-api.open-meteo.com/v1/marine"
    marine_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wave_height,wave_period,wave_direction",
        "timezone": "UTC",
    }

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,windspeed_10m,winddirection_10m",
        "timezone": "UTC",
    }

    marine = requests.get(marine_url, params=marine_params, timeout=15).json()
    weather = requests.get(weather_url, params=weather_params, timeout=15).json()
    now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    now_str = now.isoformat()

    m_times = marine.get("hourly", {}).get("time", [])
    w_times = weather.get("hourly", {}).get("time", [])

    def find_index(times, target):
        try:
            return times.index(target)
        except ValueError:
            return 0

    idx_m = find_index(m_times, now_str)
    idx_w = find_index(w_times, now_str)

    def safe_get(arr, idx, default=None):
        try:
            return arr[idx]
        except Exception:
            return default

    report = {
        "service": "surf-data-service",
        "spot": spot["name"],
        "spot_key": spot_key,
        "utc_hour": now_str + "Z",
        "wind": {
            "speed_kmh": safe_get(weather.get("hourly", {}).get("windspeed_10m", []), idx_w),
            "direction_deg": safe_get(weather.get("hourly", {}).get("winddirection_10m", []), idx_w),
        },
        "waves": {
            "height_m": safe_get(marine.get("hourly", {}).get("wave_height", []), idx_m),
            "period_s": safe_get(marine.get("hourly", {}).get("wave_period", []), idx_m),
            "direction_deg": safe_get(marine.get("hourly", {}).get("wave_direction", []), idx_m),
        },
        "temperature": {
            "air_c": safe_get(weather.get("hourly", {}).get("temperature_2m", []), idx_w),
            "water_c": None
        }
    }

    return jsonify(report)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)

