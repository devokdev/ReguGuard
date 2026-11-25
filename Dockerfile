# ReguGuard Production Containerfile
# Builds Vite React Frontend and mounts behind FastAPI static files
# Multi-stage build for minimal size and high performance

# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /ui
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source & data
COPY src/ ./src/
COPY data/ ./data/
COPY eval/ ./eval/
COPY docs/ ./docs/

# Copy built frontend assets from Stage 1 into static folder
COPY --from=frontend-builder /static ./static

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
