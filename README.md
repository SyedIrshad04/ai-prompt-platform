# PromptLab — AI Image Prompt Management Platform

A production-ready full-stack SaaS platform for managing, exploring, and analysing AI image generation prompts.

---

## Quick start

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd prompt-platform

# 2. Create your .env from the example
cp .env.example .env
# Edit .env — at minimum change DJANGO_SECRET_KEY and JWT_SECRET

# 3. Build and start all four services
docker-compose up --build

# 4. Open the app
open http://localhost
```

Sign in with `admin / admin123` or `demo / demo123` (seed credentials).
The API is available at `http://localhost/api/`.

---

## Project structure

```
prompt-platform/
├── backend/                    # Django application
│   ├── apps/
│   │   ├── prompts/            # Core feature
│   │   │   ├── models.py       # Prompt model (UUID PK, indexed)
│   │   │   ├── repositories.py # DB access layer — raw ORM only
│   │   │   ├── services.py     # Business logic + Redis view counting
│   │   │   ├── views.py        # CBVs: list, detail, analytics
│   │   │   └── validators.py   # Manual input validation (no DRF)
│   │   ├── tags/               # Tag model with M2M to Prompt
│   │   ├── auth_utils.py       # JWT helpers + login view
│   │   └── redis_client.py     # Redis connection with fallback
│   ├── config/                 # Django project settings/urls/wsgi
│   ├── seed.json               # Fixture — 6 sample prompts
│   ├── entrypoint.sh           # Wait-for-DB + migrate + gunicorn
│   └── Dockerfile
│
├── frontend/                   # Angular 17 (standalone components)
│   └── src/app/
│       ├── core/
│       │   ├── guards/         # authGuard (CanActivateFn)
│       │   ├── interceptors/   # AuthInterceptor (JWT + 401 redirect)
│       │   └── services/       # AuthService
│       ├── shared/
│       │   └── components/navbar/
│       ├── features/prompts/
│       │   ├── components/     # prompt-list, prompt-detail, prompt-create, prompt-card
│       │   ├── services/       # PromptService (all API calls)
│       │   └── models/         # Prompt interface + COMPLEXITY_LABELS
│       ├── analytics/          # Analytics dashboard component
│       ├── login/              # Login page
│       └── app.routes.ts       # Lazy-loaded routes
│
├── docker-compose.yml          # 4 services: db, redis, backend, frontend
├── .env.example
└── README.md
```

---

## Architecture decisions

### Layered backend (Controller → Service → Repository)

Every feature follows a strict three-layer separation:

- **Views** (`views.py`) — HTTP boundary only. Parse request, call service, return JSON. No ORM, no Redis.
- **Services** (`services.py`) — All business logic. Orchestrates the repository and cache. Knows nothing about HTTP.
- **Repositories** (`repositories.py`) — Raw database access only. No business logic, no Redis.

This means each layer is independently testable and replaceable (swap PostgreSQL for another DB by touching only the repository).

### Redis as source of truth for view counts

The spec requires view counts never written back to PostgreSQL on every read. The implementation:

1. `GET /api/prompts/<id>/` calls `PromptService.get_prompt()`.
2. Service calls `_increment_view(prompt_id)` which does `INCR prompt:{id}:views` in Redis.
3. The leaderboard (`prompts:leaderboard`) is a Redis sorted set updated with `ZADD` on every view, giving O(log n) inserts and O(log n + k) `ZREVRANGE` reads for the analytics dashboard.
4. If Redis is unavailable, view count returns 0 and the rest of the response is unaffected (graceful fallback).

PostgreSQL is never written on reads — only Django admin or explicit `PUT` requests modify the DB.

### Soft deletes

Prompts are never hard-deleted. `DELETE /api/prompts/<id>/` sets `is_active = False`. All list queries filter `is_active=True`. This preserves analytics history and allows recovery.

### JWT authentication

Token-based auth using `PyJWT`. The `AuthInterceptor` in Angular attaches the `Authorization: Bearer <token>` header to every outgoing request. A 401 response anywhere in the app triggers automatic logout and redirect to `/login`. The `authGuard` protects the create/edit routes client-side.

### Angular feature-based architecture

Each feature is a self-contained folder with its own components, services, and models. All components are standalone (no NgModules). Routes are lazy-loaded with `loadComponent()` — the initial bundle only contains the app shell; each page is a separate chunk fetched on demand.

### Docker networking

All services communicate over an internal `app-network` bridge. The frontend (nginx) proxies `/api/` to `http://backend:8000`, so the browser never needs to know the backend port. Only port 80 is exposed to the host.

---

## API reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/prompts/` | — | List prompts (pagination, search, filter, sort) |
| POST | `/api/prompts/` | ✓ | Create prompt |
| GET | `/api/prompts/<id>/` | — | Get prompt + increment view counter |
| PUT | `/api/prompts/<id>/` | ✓ | Update prompt |
| DELETE | `/api/prompts/<id>/` | ✓ | Soft-delete prompt |
| GET | `/api/tags/` | — | List all tags |
| GET | `/api/analytics/` | — | Top viewed (Redis leaderboard) + complexity distribution |
| POST | `/api/auth/login/` | — | Get JWT token |

Query parameters for `GET /api/prompts/`:

| Param | Example | Description |
|-------|---------|-------------|
| `search` | `?search=cyberpunk` | Full-text search on title + content |
| `complexity` | `?complexity=7` | Filter by exact complexity (1–10) |
| `tag` | `?tag=anime` | Filter by tag name |
| `sort` | `?sort=-complexity` | Sort field; prefix `-` for descending |
| `page` | `?page=2` | Page number (default 1) |
| `page_size` | `?page_size=20` | Results per page (max 50, default 10) |

---

## Trade-offs

**No DRF** — as required. All serialization, validation, and response shaping is manual. This is more code than DRF would require but gives complete control over the response shape and removes the DRF dependency. The validator functions in `validators.py` are straightforward to test.

**In-memory user store** — the JWT login uses a hardcoded dict for simplicity. A production system would have a `User` model with hashed passwords (`bcrypt`/`argon2`), email verification, and refresh tokens. Swapping this out requires only changing `auth_utils.py`.

**Redis leaderboard with `ZADD` (no GT flag on create)** — the leaderboard uses `INCR` for the view key and `ZADD` to keep the sorted set in sync. The score is always the current view count, which means the leaderboard ranking is always correct even if Redis restarts (view counts do reset on Redis restart — if you need durability, enable AOF or add a periodic sync job to write view counts back to PostgreSQL).

**No WebSockets for live view counts** — the detail page shows the view count at load time (which already includes the current request's increment). A production "live" counter would use SSE or WebSocket push. This is a reasonable trade-off given the complexity budget.

**Angular 17 standalone components** — avoids NgModule boilerplate. Every component declares its own imports. This is the recommended pattern as of Angular 17 and simplifies lazy loading.

---

## Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set env vars
export DB_HOST=localhost DB_NAME=promptdb DB_USER=promptuser DB_PASSWORD=promptpass
export REDIS_URL=redis://localhost:6379/0
export DJANGO_SECRET_KEY=dev-secret

python manage.py migrate
python manage.py loaddata seed.json
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start          # serves on http://localhost:4200
```

---

## Bonus features implemented

- **Tagging system** — Tag model, M2M relationship, filter by tag, tag chips in UI, tag suggestions on create form
- **Authentication** — JWT login, `authGuard` on protected routes, `AuthInterceptor` for token attachment and 401 handling
- **Analytics dashboard** — Top viewed prompts via Redis sorted set leaderboard, complexity distribution bar chart, Redis health status

---

## Deployment notes (Bonus D)

To deploy on Railway or Render:

1. Split into two services: backend (Python) and frontend (static + nginx or a CDN).
2. Set `DEBUG=False`, add your domain to `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`.
3. Use the managed PostgreSQL and Redis add-ons provided by the platform.
4. The `entrypoint.sh` handles migrations automatically on every deploy.
5. For the frontend, build with `npm run build` and serve the `dist/prompt-platform/browser` directory.
