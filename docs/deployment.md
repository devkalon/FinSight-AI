# FinSight AI — Deployment & Infrastructure Guide

## Quick Deployment Steps

1. **Copy Production Environment File**:
   ```bash
   cp .env.example .env
   ```
2. **Build and Launch Container Stack**:
   ```bash
   docker-compose up -d --build
   ```
3. **Verify Service Health**:
   - Backend API: `curl -f http://localhost:8000/health`
   - Frontend Web App: `http://localhost:3000`

---

## Technical Specifications
- **Reverse Proxy**: Nginx / Cloudflare with SSL/TLS termination.
- **Database**: Managed PostgreSQL 16 with `pgvector` extension.
- **Backup Strategy**: Daily `pg_dump` cron to S3/GCS bucket + WAL PITR recovery.
- **Health Monitoring**: `pg_isready` DB health check, FastAPI `/health` endpoint check, Next.js static asset compilation check.
