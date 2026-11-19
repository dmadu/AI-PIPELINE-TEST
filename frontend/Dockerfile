# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 - build the Vite/React production bundle
# ---------------------------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Vite inlines VITE_* variables at build time, so the API base URL has to be
# available as an environment variable *before* `npm run build` runs.
# The default mirrors frontend/.env.example.
ARG VITE_API_BASE_URL=http://localhost:5000/api/v1
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV NODE_ENV=production

# Copy manifests first so dependency installation is cached independently of
# the application sources.
COPY package.json package-lock.json* ./

# Reproducible install from the lockfile when it exists, plain install otherwise.
RUN if [ -f package-lock.json ]; then \
      npm ci --include=dev; \
    else \
      npm install --include=dev; \
    fi

# Copy the rest of the application sources (see .dockerignore for exclusions).
COPY . .

# Produces the static output in /app/dist (vite.config.js build.outDir).
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2 - serve the static build with nginx
# ---------------------------------------------------------------------------
FROM nginx:alpine AS runtime

# Replace the stock site configuration with the SPA-aware one.
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Only the build output is shipped - the image is fully self-contained.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
