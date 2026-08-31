# nginx/Dockerfile
# Build context MUST be the repo root (docker-compose.yml sets context: .)
# so this can reach both osm-editor/ and nginx/nginx.conf.

# ---- Stage 1: build the iD Editor fork into static files ----
FROM node:24-alpine AS frontend-build
WORKDIR /app
COPY osm-editor/package*.json ./
RUN npm ci
COPY osm-editor/ .
# IMPORTANT: verify the actual production build script name in
# osm-editor/package.json's "scripts" section - it may not be exactly
# "build" in your fork. Adjust this line if needed (e.g. "npm run dist").
RUN npm run build && npm run dist

# ---- Stage 2: nginx serving the built static files + reverse proxy ----
FROM nginx:alpine
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf