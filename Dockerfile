# Reason: slim base = smaller image, smaller attack surface. Pin the version for reproducibility.
FROM python:3.12-slim

# Reason: don't run as root inside the container (security best practice; the JD cares about security).
RUN useradd -m appuser
WORKDIR /app

# Reason: copy requirements FIRST and install, so Docker caches this layer.
# If only app.py changes later, the (slow) pip install layer is reused — faster builds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app.
COPY app.py data.json ./

USER appuser
EXPOSE 8080

# Reason: HEALTHCHECK lets Docker (and humans) see container health at a glance.
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8080/healthz')"

CMD ["python", "app.py"]