# build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# production stage
FROM node:20-alpine AS production

# Create non-root user for security
RUN addgroup --gid 1000 appgroup && \
    adduser --uid 1000 -G appgroup -D appuser

WORKDIR /app

# Copy package files and install production dependencies
COPY --chown=appuser:appgroup package*.json ./
RUN npm ci --omit dev

# Copy built application
COPY --chown=appuser:appgroup --from=build /app/build ./build

# Switch to non-root user
USER appuser

EXPOSE 3000
ENV HOST=0.0.0.0
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "build"]
