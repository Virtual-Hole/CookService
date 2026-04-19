# CookService

## Redis (Docker)

Loyiha `REDIS_URL` orqali Redis cache ishlatadi.

1. Redis container ishga tushirish:
```bash
docker compose up -d redis
```

2. Tekshirish:
```bash
docker compose ps
docker compose logs -f redis
```

`.env` ichida default:
```env
REDIS_URL=redis://127.0.0.1:6379/1
```
