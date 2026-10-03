# =========================
# Stage 1: Build dependencies
# =========================
FROM python:3.11-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM rayproject/ray:2.40.0-py311

WORKDIR /home/ray/app

# Copy only installed Python packages
COPY --from=builder /install /usr/local

# Copy application
COPY app/app.py ./
COPY app/static ./static

# Allow Ray Serve to resolve app:app
ENV PYTHONPATH=/home/ray/app
