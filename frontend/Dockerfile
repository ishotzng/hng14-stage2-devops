# Stage 1: install dependencies
FROM node:20-slim AS builder
WORKDIR /build
COPY package*.json ./
RUN npm install --omit=dev

# Stage 2: final lean image
FROM node:20-slim
WORKDIR /app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /build/node_modules ./node_modules
COPY app.js .
COPY views ./views

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', r => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "app.js"]