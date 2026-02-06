import os
import time
import requests
import datetime

ENV = os.getenv("ENVIRONMENT", "DEV")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:5000")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "dev-token")
SCHEDULE_SECONDS = int(os.getenv("SCHEDULE_SECONDS", "60"))  # DEV: 60s

def run_once():
    url = f"{GATEWAY_URL}/internal/send-daily?spot=carcavelos"
    headers = {"X-Internal-Token": INTERNAL_TOKEN}

    print("====================================")
    print(f"[scheduler] ENV={ENV}")
    print(f"[scheduler] POST {url}")

    for attempt in range(5):
        try:
            r = requests.post(url, headers=headers, timeout=20)
            print(f"[scheduler] status={r.status_code}")
            print(f"[scheduler] body={r.text}")
            return
        except Exception as e:
            print(f"[scheduler] tentativa {attempt+1}/5 falhou: {e}")
            time.sleep(5)

    print("[scheduler] gateway indisponível após retries.")


def main():
    print(f"[scheduler] iniciado. intervalo={SCHEDULE_SECONDS}s")
    while True:
        run_once()
        time.sleep(SCHEDULE_SECONDS)

if __name__ == "__main__":
    main()

