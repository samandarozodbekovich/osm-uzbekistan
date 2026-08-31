# osm_api/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# GeoDjango needs these system libraries (GDAL/GEOS/PROJ) - without them
# "python manage.py" fails immediately with a GDAL/GEOS not found error.
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Collect static files at build time (admin CSS/JS, DRF browsable API, etc.)
# Safe to fail here if settings aren't fully configured yet during first build.
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "osm_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]