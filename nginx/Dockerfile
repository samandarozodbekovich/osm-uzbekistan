# nginx/Dockerfile
#
# Does NOT build the frontend. Requires osm-editor/dist to already exist
# and be up to date BEFORE running "docker compose build" - build it
# locally first:
#
#   cd osm-editor
#   npm run build
#   npm run dist        <-- do not skip this one (produces iD.min.js)
#   cd ..
#   scp -r osm-editor/dist user@SERVER_IP:/path/to/map_work/osm-editor/dist
#
# Then on the server:
#   docker compose up -d --build

FROM nginx:alpine
COPY osm-editor/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf






# # nginx/Dockerfile
# # Build context MUST be the repo root (docker-compose.yml sets context: .)
# # so this can reach both osm-editor/ and nginx/nginx.conf.

# # ---- Stage 1: build the iD Editor fork into static files ----
# FROM node:24-alpine AS frontend-build
# WORKDIR /app
# COPY osm-editor/package*.json ./
# RUN npm ci
# COPY osm-editor/ .
# # IMPORTANT: verify the actual production build script name in
# # osm-editor/package.json's "scripts" section - it may not be exactly
# # "build" in your fork. Adjust this line if needed (e.g. "npm run dist").
# RUN npm run build && npm run dist

# # ---- Stage 2: nginx serving the built static files + reverse proxy ----
# FROM nginx:alpine
# COPY --from=frontend-build /app/dist /usr/share/nginx/html
# COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf