from flask import Flask, jsonify
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


@app.get("/api")
def api():
    r = requests.get("http://data-service:5001/data", timeout=3)
    return jsonify({
        "service": "gateway",
        "status": "ok",
        "from_data_service": r.json()
    })

@app.get("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
