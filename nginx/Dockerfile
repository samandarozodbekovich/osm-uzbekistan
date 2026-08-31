# nginx/Dockerfile
# Build context MUST be the repo root (docker-compose.yml sets context: .)
# so this can reach both osm-editor/ and nginx/nginx.conf.

# ---- Stage 1: build the iD Editor fork into static files ----
FROM node:24-alpine AS frontend-build
WORKDIR /app
COPY osm-editor/package*.json ./
RUN npm ci
COPY osm-editor/ .
RUN npm run build && npm run dist

# ---- Stage 2: nginx serving the built static files + reverse proxy ----
FROM nginx:alpine
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Self-signed SSL certificate (no domain yet). Browsers will show a
# "not secure" warning until you switch to a real Let's Encrypt cert
# once you have a domain - functionally HTTPS works fine either way.
RUN apk add --no-cache openssl && \
    mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/CN=localhost"