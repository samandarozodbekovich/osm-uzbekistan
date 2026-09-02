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

# ── SERVER: https://map.getplace.uz ← docker-compose.yml dan o'zgaradi ───────
# (docker-compose.yml dagi args qismida qayta yozing, bu yerda o'zgartirmang)

COPY osm-editor/package*.json ./
RUN npm ci
COPY osm-editor/ .

# Baked-in API connection config (osm-editor/.env ni build vaqtida qayta yozadi)
RUN printf '%s\n' \
    "ID_API_CONNECTION_URL=${ID_API_CONNECTION_URL}" \
    "ID_API_CONNECTION_API_URL=${ID_API_CONNECTION_API_URL}" \
    "ID_API_CONNECTION_CLIENT_ID=${ID_API_CONNECTION_CLIENT_ID}" \
    > .env

RUN npm run build && npm run dist

# =============================================================================
# Stage 2: nginx
# =============================================================================
FROM nginx:alpine

COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# LOCAL: SSL sertifikat kerak emas — nginx.conf faqat port 80 ishlatadi.
# SERVER: sertifikat host mashinasida /etc/letsencrypt da turadi va
#         docker-compose.yml dagi volumes orqali mount qilinadi.
#         Serverda ishga tushirishdan oldin:
#           sudo certbot certonly --standalone -d map.getplace.uz
