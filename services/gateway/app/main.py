from flask import Flask, jsonify
import requests

app = Flask(__name__)

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
