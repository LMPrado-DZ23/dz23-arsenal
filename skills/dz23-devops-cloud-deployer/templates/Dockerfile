# syntax=docker/dockerfile:1.7
# Dockerfile de referência: multi-stage, non-root, base pinada por digest.
# Substitua o digest da base pelo vigente do seu registry.

ARG NODE_VERSION=22
FROM node:${NODE_VERSION}-slim@sha256:0000000000000000000000000000000000000000000000000000000000000000 AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts

FROM node:${NODE_VERSION}-slim@sha256:0000000000000000000000000000000000000000000000000000000000000000 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build && npm prune --omit=dev

FROM gcr.io/distroless/nodejs22-debian12:nonroot@sha256:0000000000000000000000000000000000000000000000000000000000000000 AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080
ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA}

COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./package.json

USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/nodejs/bin/node", "dist/server.js"]
