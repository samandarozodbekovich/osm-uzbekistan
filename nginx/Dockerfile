# nginx/Dockerfile
# Build context: repo root (docker-compose.yml sets context: .)

# =============================================================================
# Stage 1: iD Editor frontend build
# =============================================================================
FROM node:24-alpine AS frontend-build
WORKDIR /app

# ── LOCAL: http://localhost ← ACTIVE ─────────────────────────────────────────
ARG ID_API_CONNECTION_URL=http://localhost
ARG ID_API_CONNECTION_API_URL=http://localhost
ARG ID_API_CONNECTION_CLIENT_ID=dummy-client-id

# ── SERVER: https://map.getplace.uz ← overridden from docker-compose.yml ─────
# (override in the args section of docker-compose.yml, not here)

COPY osm-editor/package*.json ./
RUN npm ci
COPY osm-editor/ .

# Baked-in API connection config (overwrites osm-editor/.env at build time)
RUN printf '%s\n' \
    "ID_API_CONNECTION_URL=${ID_API_CONNECTION_URL}" \
    "ID_API_CONNECTION_API_URL=${ID_API_CONNECTION_API_URL}" \
    "ID_API_CONNECTION_CLIENT_ID=${ID_API_CONNECTION_CLIENT_ID}" \
    > .env

RUN npm run build && npm run dist

# default-custom-data.js: bakes in the Martin tiles URL (from the build arg).
# {z}/{x}/{y} is literal here, not shell brace expansion.
RUN printf '(function(){var S="settings-custom-data-url",V="settings-custom-data-url-version",VER="2",URL="%s/tiles/basemap_tiles/{z}/{x}/{y}";try{var v=localStorage.getItem(V),s=localStorage.getItem(S);if(!s||v!==VER){localStorage.setItem(S,URL);localStorage.setItem(V,VER)}}catch(e){console.warn("default-custom-data.js:",e)}})();\n' \
    "${ID_API_CONNECTION_URL}" > dist/default-custom-data.js

# =============================================================================
# Stage 2: nginx
# =============================================================================
FROM nginx:alpine

COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# npm build sometimes leaves directories at 700 or files at 600 — the nginx
# worker (nginx user) then can't read them and try_files falls back to
# index.html. a+rX adds read to files and read+execute to directories.
RUN chmod -R a+rX /usr/share/nginx/html

# LOCAL: no SSL certificate needed — nginx.conf only uses port 80.
# SERVER: the certificate lives on the host at /etc/letsencrypt and is
#         mounted via the volumes in docker-compose.yml.
#         Before starting on the server:
#           sudo certbot certonly --standalone -d map.getplace.uz
