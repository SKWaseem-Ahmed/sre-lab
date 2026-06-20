import json
import logging
import os
import random
import time
from pythonjsonlogger import jsonlogger
from flask import Flask, jsonify, render_template_string, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# --- Structured JSON logging ---
# Reason: Fluent Bit / Splunk parse JSON logs into fields automatically. Plain-text logs
# force you to write fragile regex parsers later. Structured-from-the-start is an SRE habit.
logger = logging.getLogger("app")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = Flask(__name__)

# --- Prometheus metrics ---
# Reason: a Counter only goes up (good for "total requests"); a Histogram buckets values
# (good for latency, lets Grafana compute p95/p99). These two cover most app-level SLIs.
REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])

DATA_FILE = os.environ.get("DATA_FILE", "data.json")

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

@app.route("/")
def index():
    start = time.time()
    data = load_data()
    # Render a tiny HTML page that lists the dummy data (the "webapp" requirement).
    html = """
    <h1>SRE Lab — Visa Card Catalog</h1>
    <table border=1 cellpadding=6>
      <tr><th>ID</th><th>Name</th><th>Tier</th><th>Annual Fee</th></tr>
      {% for p in products %}
      <tr><td>{{p.id}}</td><td>{{p.name}}</td><td>{{p.tier}}</td><td>${{p.annual_fee}}</td></tr>
      {% endfor %}
    </table>
    """
    resp = render_template_string(html, products=data["products"])
    LATENCY.labels("/").observe(time.time() - start)
    REQUESTS.labels("GET", "/", "200").inc()
    logger.info("served index", extra={"endpoint": "/", "count": len(data["products"])})
    return resp

@app.route("/api/products")
def api_products():
    start = time.time()
    data = load_data()
    LATENCY.labels("/api/products").observe(time.time() - start)
    REQUESTS.labels("GET", "/api/products", "200").inc()
    logger.info("served api", extra={"endpoint": "/api/products"})
    return jsonify(data["products"])

@app.route("/healthz")
def healthz():
    # Reason: Kubernetes uses this for liveness/readiness probes. Keep it cheap and dependency-free.
    return jsonify(status="ok"), 200

@app.route("/flaky")
def flaky():
    # Reason: a deliberately unreliable endpoint we'll use in Phase 9 to generate errors/alerts.
    start = time.time()
    if random.random() < 0.5:
        REQUESTS.labels("GET", "/flaky", "500").inc()
        LATENCY.labels("/flaky").observe(time.time() - start)
        logger.error("flaky endpoint failed", extra={"endpoint": "/flaky"})
        return jsonify(error="random failure"), 500
    REQUESTS.labels("GET", "/flaky", "200").inc()
    LATENCY.labels("/flaky").observe(time.time() - start)
    return jsonify(status="lucky"), 200

@app.route("/metrics")
def metrics():
    # Reason: Prometheus scrapes this endpoint. CONTENT_TYPE_LATEST is the format it expects.
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    logger.info("starting app", extra={"port": 8080})
    app.run(host="0.0.0.0", port=8080)