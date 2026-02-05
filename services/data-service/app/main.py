from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.get("/data")
def data():
    return jsonify({
        "service": "data-service",
        "message": "ola do microservico 2",
        "utc": datetime.datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
