from flask import Flask, jsonify, request
import os
import datetime

app = Flask(__name__)
ENV = os.getenv("ENVIRONMENT", "DEV")

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "notification-service", "env": ENV})

@app.post("/send")
def send():
    payload = request.get_json(force=True) or {}

    channel = payload.get("channel", "log")
    to = payload.get("to", "unknown")
    subject = payload.get("subject", "")
    message = payload.get("message", "")

    print("==== NOTIFICATION SEND ====")
    print("UTC:", datetime.datetime.utcnow().isoformat())
    print("ENV:", ENV)
    print("CHANNEL:", channel)
    print("TO:", to)
    print("SUBJECT:", subject)
    print("MESSAGE:\n", message)
    print("===========================")

    return jsonify({"status": "queued", "channel": channel, "to": to, "env": ENV})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002) # nosec B104

