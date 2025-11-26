from flask import Flask, jsonify
import os, math, time

app = Flask(__name__)

def cpu_burn(ms=150):
    end = time.time() + (ms/1000.0)
    while time.time() < end:
        math.sqrt(12345.6789)

@app.route("/patient-summary")
def patient_summary():
    cpu_burn(150)
    pod = os.getenv("HOSTNAME", "unknown")
    return jsonify({"status": "ok", "pod": pod})

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
