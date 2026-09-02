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

# NOTE: collectstatic is intentionally NOT run here at build time.
# The compose file mounts a named volume at /app/staticfiles, which
# would hide anything written here during the image build. Instead,
# entrypoint.sh runs collectstatic at container startup, after the
# volume is already mounted.

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]