from flask import send_from_directory, Flask, jsonify, request, render_template_string
import os
import requests

app = Flask(__name__)

ENABLE_OTEL = os.getenv("ENABLE_OTEL", "false").lower() == "true"

if ENABLE_OTEL:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        resource = Resource.create({"service.name": "gateway"})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        # Exportador OTLP → Jaeger container
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://jaeger:4317",
            insecure=True
        )

        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()

        print("[OTEL] enabled with OTLP exporter → jaeger:4317")

    except Exception as e:
        print(f"[OTEL] failed to initialize: {e}")



ENV = os.getenv("ENVIRONMENT", "DEV")

SURF_DATA_URL = os.getenv("SURF_DATA_URL", "http://surf-data-service:5001")

def ui_home():
    html = """
    <!doctype html>
    <html>
    <head><meta charset="utf-8"><title>SurfPulse</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
      <h1>SurfPulse Platform</h1>
      <p>Status API:</p>
      <ul>
        <li>/health</li>
        <li>/api/report?spot=carcavelos</li>
      </ul>
      <form method="get" action="/api/report">
        <label>Spot:</label>
        <select name="spot">
          <option value="carcavelos">carcavelos</option>
          <option value="guincho">guincho</option>
          <option value="caparica">caparica</option>
        </select>
        <button type="submit">Gerar Report</button>
      </form>
    </body></html>
    """
    return render_template_string(html)

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
    app.run(host="0.0.0.0", port=5000)  # nosec B104

# --- Frontend (React build) served by Flask ---
@app.get("/")
def serve_frontend():
    return send_from_directory("static", "index.html")

@app.get("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("static/assets", filename)

# SPA fallback: any other route returns the frontend
@app.get("/<path:path>")
def spa_fallback(path):
    # if it is a real file in /static, serve it
    try:
        return send_from_directory("static", path)
    except Exception:
        return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104
