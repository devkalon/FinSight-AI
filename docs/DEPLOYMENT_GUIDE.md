# FinSight AI — Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying FinSight AI in a secure, production-ready environment utilizing Docker, Managed PostgreSQL (with `pgvector`), FastAPI ASGI Gateway, and Next.js Frontend.

---

## Architecture Overview

```
                          [ Client Browser / HTTPS ]
                                     │
                                     ▼
                    [ Nginx / Cloudflare Reverse Proxy ]
                          (SSL / TLS Termination)
                                  │     │
                 ┌────────────────┘     └────────────────┐
                 ▼                                       ▼
    [ Next.js Frontend Container ]         [ FastAPI Gateway Container ]
        (Port 3000 / SSR Build)                 (Port 8000 / Uvicorn)
                                                         │
                                                         ▼
                                            [ Managed PostgreSQL DB ]
                                             (Port 5432 / pgvector)
```

---

## 1. Environment Variable Setup (`.env`)

Copy `.env.example` to `.env` and fill in secure credentials:

```bash
cp .env.example .env
```

### Essential Production Variables:
```env
ENVIRONMENT="production"
DEBUG=False
SECRET_KEY="<GENERATE_RANDOM_32_BYTE_HEX_KEY>" # openssl rand -hex 32
DATABASE_URL="postgresql+asyncpg://finsight_user:<SECURE_PASSWORD>@managed-db-host:5432/finsight_db"
BACKEND_CORS_ORIGINS='["https://finsight.app","https://api.finsight.app"]'
```

> [!CAUTION]
> Never commit `.env` or plain-text database credentials to Git repositories.

---

## 2. Managed Database & Migration Setup

### Managed PostgreSQL Configuration:
1. Provision a PostgreSQL 16+ instance on AWS RDS, GCP Cloud SQL, or DigitalOcean Managed Databases.
2. Enable the `pgvector` extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Initialize tables using SQLAlchemy migrations or backend auto-init:
   ```bash
   python -c "import asyncio; from backend.app.core.database import init_db; asyncio.run(init_db())"
   ```

---

## 3. Database Backup Strategy

- **Daily Automated Snapshots**:
  Configure automated `pg_dump` cron backups to S3/GCS bucket:
  ```bash
  0 2 * * * pg_dump -U finsight_user -h managed-db-host -d finsight_db | gzip > /backups/finsight_$(date +\%F).sql.gz
  ```
- **Point-in-Time Recovery (PITR)**: Enable Write-Ahead Logging (WAL) archiving with a 7-day retention window on managed database providers.

---

## 4. Production Docker Deployment

Deploy all services using Docker Compose:

```bash
docker-compose up -d --build
```

### Health Check Verification:
- **Backend API**: `curl -f http://localhost:8000/health`
- **Frontend App**: `curl -f http://localhost:3000`
- **PostgreSQL DB**: `docker exec finsight_postgres pg_isready -U finsight_user`

---

## 5. SSL / TLS HTTPS Termination (Nginx Reverse Proxy)

Example Nginx server block:

```nginx
server {
    listen 443 ssl http2;
    server_name finsight.app;

    ssl_certificate /etc/letsencrypt/live/finsight.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/finsight.app/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 6. Public Demo Configuration

For public demonstrations, load the synthetic dataset seeder:

```bash
python -c "import asyncio; from backend.app.core.database import seed_demo_data; asyncio.run(seed_demo_data())"
```

> [!NOTE]
> The demo dataset uses 100% synthetic transactions and mock identities. Zero real financial data is exposed.
