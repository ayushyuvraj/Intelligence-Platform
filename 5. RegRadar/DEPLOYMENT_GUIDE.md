# RegRadar Deployment Guide

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** April 18, 2026

---

## Overview

RegRadar is a production-ready AI-powered regulatory intelligence platform for India. This guide covers deployment, configuration, and operational procedures.

---

## Pre-Deployment Checklist

### Infrastructure
- [ ] Server with Docker and Docker Compose installed
- [ ] Minimum 2GB RAM, 10GB disk space
- [ ] Outbound HTTPS access (for Gemini API, government websites)
- [ ] SMTP server access (for email digests - Phase 2)
- [ ] Database backups configured

### Configuration
- [ ] Environment variables configured (.env file)
- [ ] SSL certificates obtained (production)
- [ ] DNS records configured
- [ ] CDN configured (optional)

### Monitoring & Operations
- [ ] Sentry project created and configured
- [ ] Logging aggregation setup (e.g., ELK stack)
- [ ] Alerting rules configured
- [ ] Oncall rotation established

### Testing
- [ ] End-to-end testing completed
- [ ] Load testing passed (100 concurrent users)
- [ ] Security audit passed
- [ ] Accessibility audit passed (WCAG AA)

---

## Environment Setup

### 1. Create `.env` File

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=sqlite:///./regradar.db
# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:password@host:5432/regradar

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# URLs
BACKEND_URL=https://api.regradar.io
FRONTEND_URL=https://regradar.io

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_here

# Scraper
SCRAPER_ENABLED=true
SCRAPER_INTERVAL_HOURS=6

# Email (Phase 2)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 2. Security Best Practices

**Never commit `.env` file to version control:**
```bash
echo ".env" >> .gitignore
```

**Restrict file permissions:**
```bash
chmod 600 .env
```

**Use secrets management for production:**
- AWS Secrets Manager
- HashiCorp Vault
- GCP Secret Manager
- Azure Key Vault

---

## Local Development

### Start Services

```bash
docker-compose up --build
```

### Access Points
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Seed Database

```bash
docker-compose exec backend python scripts/seed_data.py
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Production Deployment

### Option 1: Docker Compose (Single Server)

```bash
# 1. Clone repository
git clone https://github.com/ayushyuvraj/regradar.git
cd regradar

# 2. Create .env file
cp .env.example .env
# Edit .env with production values

# 3. Build images
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Seed data
docker-compose exec backend python scripts/seed_data.py

# 6. Verify health
curl http://localhost:8000/health
curl http://localhost:3000/
```

### Option 2: Kubernetes Deployment (Multi-Server)

Prerequisites: Kubernetes cluster (EKS, GKE, AKS, or self-managed)

```bash
# 1. Build and push images to registry
docker build -t your-registry/regradar-backend:1.0.0 -f Dockerfile .
docker build -t your-registry/regradar-frontend:1.0.0 -f frontend.Dockerfile .
docker push your-registry/regradar-backend:1.0.0
docker push your-registry/regradar-frontend:1.0.0

# 2. Create Kubernetes manifests (see k8s/ directory)
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 3. Verify deployment
kubectl get pods -n regradar
kubectl logs -f deployment/regradar-backend -n regradar
```

### Option 3: Managed Platforms

**Railway.app:**
```bash
# Connect repository and add environment variables
# Platform auto-detects docker-compose.yml and deploys
```

**Heroku:**
```bash
# Uses Procfile for configuration
heroku create regradar
heroku config:set GEMINI_API_KEY=xxx
git push heroku main
```

**AWS ECS:**
```bash
# Push images to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin your-registry.dkr.ecr.region.amazonaws.com
docker push your-registry/regradar-backend:1.0.0

# Create ECS task definitions and service via console or CLI
```

---

## Post-Deployment

### 1. Verify Services

```bash
# Health checks
curl https://api.regradar.io/health -H "X-Correlation-ID: test"
curl https://regradar.io/

# Check logs
docker logs regradar-backend | tail -20
docker logs regradar-frontend | tail -20
```

### 2. Initialize Monitoring

```bash
# Sentry
https://sentry.io/ → Create project → Copy DSN to .env

# Application metrics
# Check Prometheus/Grafana dashboards
```

### 3. Backup Database

```bash
# Daily automated backups
sqlite3 regradar.db ".backup '/backups/regradar-$(date +%Y%m%d).db'"

# For PostgreSQL
pg_dump regradar > /backups/regradar-$(date +%Y%m%d).sql
```

### 4. Configure Monitoring Alerts

**Critical Alerts:**
- API error rate > 1%
- API response time p95 > 1 second
- Database connection failures
- Scraper failures for 12+ hours
- Disk usage > 90%

**Warning Alerts:**
- Gemini API quota > 80%
- Memory usage > 75%
- Response time p95 > 500ms

---

## Scaling & Performance

### Database Optimization

For high traffic, migrate from SQLite to PostgreSQL:

```bash
# 1. Dump SQLite
sqlite3 regradar.db ".dump" > backup.sql

# 2. Set up PostgreSQL
docker run -d \
  --name regradar-db \
  -e POSTGRES_DB=regradar \
  -e POSTGRES_PASSWORD=secure_password \
  postgres:15

# 3. Restore data
psql -U postgres -d regradar < backup.sql

# 4. Update DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost:5432/regradar
```

### Caching Strategy

```python
# Enable Redis caching for frequently accessed data
CACHE_BACKEND=redis://localhost:6379/0
CACHE_TTL_SECONDS=3600
```

### Load Balancing

```nginx
# Nginx upstream configuration
upstream backend {
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}

server {
    listen 80;
    location /api {
        proxy_pass http://backend;
    }
}
```

---

## Disaster Recovery

### Backup Strategy

**Daily Backups:**
```bash
0 2 * * * sqlite3 /app/regradar.db ".backup '/backups/regradar-$(date +\%Y\%m\%d).db'"
```

**Weekly Full Snapshots:**
```bash
0 3 * * 0 tar -czf /backups/regradar-$(date +%Y%m%d).tar.gz /app/
```

**Retention Policy:**
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 12 months

### Recovery Procedure

**RTO:** < 1 hour  
**RPO:** < 1 hour

```bash
# 1. Stop services
docker-compose down

# 2. Restore from backup
sqlite3 regradar.db < /backups/regradar-backup.sql

# 3. Restart services
docker-compose up -d

# 4. Verify data
curl http://localhost:8000/api/stats
```

---

## Troubleshooting

### API Not Responding

```bash
# 1. Check container status
docker ps | grep regradar-backend

# 2. View logs
docker logs regradar-backend --tail=100

# 3. Check port binding
netstat -tulpn | grep 8000

# 4. Restart service
docker-compose restart backend
```

### Database Issues

```bash
# 1. Check database file exists
ls -lh regradar.db

# 2. Verify permissions
chmod 666 regradar.db

# 3. Repair database
sqlite3 regradar.db "PRAGMA integrity_check;"

# 4. Restore from backup if corrupted
sqlite3 regradar.db < /backups/regradar-backup.sql
```

### Memory Leak

```bash
# 1. Monitor memory usage
docker stats regradar-backend

# 2. Check for large queries
# Review logs for long-running operations

# 3. Restart service (temporary fix)
docker-compose restart backend

# 4. Implement memory limits in docker-compose.yml
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error rates
- Check API response times
- Verify scraper runs completed

**Weekly:**
- Review logs for patterns
- Backup database
- Check disk usage

**Monthly:**
- Security audit
- Performance review
- Update dependencies

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Deploy with zero downtime
docker-compose up -d --force-recreate

# Verify health
docker-compose exec backend python -m pytest
```

---

## Support & Escalation

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| API returns 503 | Database unavailable | Restart backend, check DB file |
| Slow feed load | Large result set | Add pagination, implement caching |
| Scraper fails | Government website down | Check website status, retry later |
| High memory usage | Memory leak | Restart service, review code |
| Disk full | Large database | Archive old data, expand disk |

### Escalation Path

1. **Level 1:** Automated alerts → Review logs
2. **Level 2:** Manual investigation → Check metrics
3. **Level 3:** Engineering team → Code review & fix
4. **Level 4:** Architect → Infrastructure changes

---

## Security Checklist

- [ ] HTTPS enforced (Strict-Transport-Security header)
- [ ] Secrets not in code or logs
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] Rate limiting enabled
- [ ] Security headers present
- [ ] Monitoring and alerting active
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Docker Best Practices](https://docs.docker.com/develop/development-best-practices/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [RegRadar CLAUDE.md](./CLAUDE.md)

---

**Last Updated:** April 18, 2026  
**Owner:** Ayush Yuvraj  
**Status:** Production Ready
