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

## Environment

Server uchun tavsiya:

1. `.env.example` dan nusxa oling:
```bash
cp .env.example .env
```
2. `.env` ichidagi qiymatlarni productionga moslang.

Minimal muhim envlar:
```env
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=api.example.com
CSRF_TRUSTED_ORIGINS=https://api.example.com
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://app.example.com,http://localhost:3000
DB_ENGINE=django.db.backends.postgresql
DB_NAME=cookservice
DB_USER=postgres
DB_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/1
```
