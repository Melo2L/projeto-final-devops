from flask import Flask, jsonify, request
import os
import requests

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

resource = Resource.create({"service.name": "gateway"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

ENV = os.getenv("ENVIRONMENT", "DEV")

SURF_DATA_URL = os.getenv("SURF_DATA_URL", "http://surf-data-service:5001")

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "gateway", "env": ENV})

@app.get("/api/report")
def api_report():
    spot = request.args.get("spot", "carcavelos")

    r = requests.get(f"{SURF_DATA_URL}/forecast", params={"spot": spot}, timeout=15)
    return jsonify({
        "service": "gateway",
        "env": ENV,
        "spot": spot,
        "report": r.json()
    })

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "dev-token")
NOTIFY_URL = os.getenv("NOTIFY_URL", "http://notification-service:5002")

SUBSCRIBERS = [
    {"channel": "whatsapp", "to": "+351900000000"},
    {"channel": "email", "to": "cliente@exemplo.com"},
]

def format_message(report: dict) -> str:
    wind = report.get("wind", {})
    waves = report.get("waves", {})
    temp = report.get("temperature", {})

    return (
        f"🏄 SurfPulse - {report.get('spot')} (UTC {report.get('utc_hour')})\n\n"
        f"💨 Vento: {wind.get('speed_kmh')} km/h | Dir: {wind.get('direction_deg')}°\n"
        f"🌊 Ondas: {waves.get('height_m')} m | Período: {waves.get('period_s')} s | Dir: {waves.get('direction_deg')}°\n"
        f"🌡️ Temp ar: {temp.get('air_c')} °C\n"
        f"ℹ️ Nota: Maré e temp da água não incluídas (API pública sem chave).\n"
    )

@app.post("/internal/send-daily")
def send_daily():
    token = request.headers.get("X-Internal-Token", "")
    if token != INTERNAL_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    spot = request.args.get("spot", "carcavelos")

    r = requests.get(f"{SURF_DATA_URL}/forecast", params={"spot": spot}, timeout=15)
    report = r.json()

    msg = format_message(report)

    results = []
    for sub in SUBSCRIBERS:
        payload = {
            "channel": sub["channel"],
            "to": sub["to"],
            "subject": f"SurfPulse - {report.get('spot')}",
            "message": msg
        }
        s = requests.post(f"{NOTIFY_URL}/send", json=payload, timeout=15)
        results.append(s.json())

    return jsonify({"status": "sent", "count": len(results), "results": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
