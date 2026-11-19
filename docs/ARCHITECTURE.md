# Architecture

> This is the single, authoritative architecture document for the project.
> (Previously tracked as `docs/ARCHITECTURE.md` - renamed to `docs/architecture.md`;
> content preserved.)

## Overview
A responsive single-page React 19 frontend (Vite, MUI, Tailwind, React Router DOM) talks over a REST/JSON API to a Flask 3 backend that persists users in PostgreSQL 16 via SQLAlchemy and Flask-Migrate. The backend is an API-only application factory exposing /api/v1 endpoints, using Flask-Bcrypt for password hashing and Flask-JWT-Extended for access tokens. The frontend stores the JWT in memory plus localStorage, attaches it as a Bearer header, and guards the /dashboard route. Both services run as separate Docker images orchestrated by Docker Compose alongside a postgres service.

## Technology Stack
- Python 3.11, Flask 3.x - backend API (application factory + blueprints)
- Flask-SQLAlchemy 3.x + SQLAlchemy 2.x - ORM
- Flask-Migrate 4.x (Alembic) - schema migrations
- Flask-Bcrypt - password hashing (REQ-007)
- Flask-JWT-Extended 4.x - JWT issuance/validation (REQ-011)
- Flask-Cors - frontend origin is a different port; required for browser API calls
- email-validator - RFC-compliant server-side email format check (REQ-005)
- python-dotenv - load .env in local (non-Docker) runs
- gunicorn - WSGI server used in the backend container
- psycopg2-binary - PostgreSQL driver
- pytest + pytest-flask - backend tests
- React 19 + Vite 5 (JavaScript, no TypeScript) - frontend build/dev server
- Material UI 6 + @emotion - components; Tailwind CSS 3 - layout/responsive utilities
- React Router DOM 7 - client routing
- axios - single configured HTTP client with auth interceptor
- Vitest + React Testing Library - frontend tests
- nginx:alpine - serves the built frontend in its container
- PostgreSQL 16, Docker, Docker Compose
- Jinja2/Bootstrap from the stack are NOT used: the UI is React-only; no server-rendered pages exist

## Folder Structure
- backend/ - Flask service root (Dockerfile, requirements.txt, wsgi.py, .env.example, pytest.ini)
- backend/app/ - application package (__init__.py holds create_app, extensions.py, config.py)
- backend/app/models/ - SQLAlchemy models (user.py)
- backend/app/api/ - blueprints: auth.py (register/login/me), health.py
- backend/app/schemas/ - request validation helpers (auth_schemas.py)
- backend/app/utils/ - errors.py, validators.py, responses.py
- backend/migrations/ - Flask-Migrate/Alembic output
- backend/tests/ - pytest suite (conftest.py, test_auth.py, test_validators.py)
- frontend/ - React service root (Dockerfile, nginx.conf, vite.config.js, tailwind.config.js, index.html, .env.example)
- frontend/src/pages/ - Home.jsx, About.jsx, Contact.jsx, Register.jsx, Dashboard.jsx, NotFound.jsx
- frontend/src/components/ - Navbar.jsx, Layout.jsx, LoginForm.jsx, RegisterForm.jsx, ProtectedRoute.jsx, Alert.jsx
- frontend/src/context/ - AuthContext.jsx
- frontend/src/api/ - client.js, auth.js
- frontend/src/utils/ - validators.js
- frontend/src/tests/ - Vitest specs
- docs/ - architecture.md and any generated docs
- docker-compose.yml, .env.example, Readme.md - repo root

## Data Model
- User: id (Integer PK), username (String(50), unique, not null, case-insensitive uniqueness enforced by storing as given and querying with func.lower), email (String(255), unique, not null, stored lowercased), password_hash (String(255), not null), created_at (DateTime, UTC, default now), updated_at (DateTime, UTC, onupdate now); table name 'users'; no relationships (single entity).
- User methods: set_password(raw) uses bcrypt.generate_password_hash; check_password(raw); to_dict() returns id, username, email, created_at only - never password_hash.
- No other entities; JWTs are stateless so no session/token table.

## API Conventions
- Base path /api/v1; plural/lowercase kebab paths; endpoints: POST /api/v1/auth/register, POST /api/v1/auth/login, GET /api/v1/auth/me, GET /api/v1/health.
- JSON only, in and out; request bodies are flat objects (register: email, username, password; login: identifier, password).
- Success: HTTP 200/201 with {"data": {...}} envelope; register returns 201 with the user; login returns 200 with access_token and user.
- Errors: {"error": {"code": "<MACHINE_CODE>", "message": "<human text>", "fields": {"<field>": "<message>"}}}; fields omitted when not field-specific.
- Status codes: 400 VALIDATION_ERROR, 401 INVALID_CREDENTIALS / TOKEN_MISSING / TOKEN_INVALID, 404 NOT_FOUND, 409 DUPLICATE_USERNAME or DUPLICATE_EMAIL, 500 INTERNAL_ERROR.
- Auth: Bearer JWT in Authorization header; access token only, 1 hour expiry, identity = str(user.id); protected routes use @jwt_required().
- Login accepts a single 'identifier' field matched against email (lowercased) or username; failures always return the generic message "Invalid username/email or password" to avoid user enumeration.
- CORS allowed origin comes from the FRONTEND_ORIGIN env var; all validation runs server-side regardless of client checks.

## Coding Standards
- Python: PEP 8, snake_case functions/modules, PascalCase classes, 4-space indent, max line 100; JS: camelCase values, PascalCase components/files in components and pages.
- Backend layering: blueprint route parses/validates input -> model/db work -> returns envelope; no SQL or bcrypt calls in route bodies beyond model helpers.
- Validation lives in backend/app/utils/validators.py (validate_email_format, validate_password, validate_username) and is mirrored, never replaced, by frontend/src/utils/validators.js.
- Password rule (shared constant): >=8 chars, >=1 uppercase, >=1 digit, >=1 special from !@#$%^&*()-_=+[]{};:,.<>?/|~; one message per failed rule in error.fields.password.
- Errors raised as ApiError(code, message, status, fields) from utils/errors.py; a single app-level errorhandler converts ApiError, HTTPException and Exception into the error envelope.
- Logging via app.logger (StreamHandler, INFO in prod, DEBUG in dev); log registration/login outcomes with username only - never passwords, hashes or tokens.
- Config via environment only (config.py classes Development/Production/Testing); required vars: DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY, FRONTEND_ORIGIN; no secrets committed.
- Tests: pytest for backend (SQLite in-memory via TestingConfig, covering validation, duplicate signup, login by username/email, protected route without token); Vitest + RTL for navigation, form validation and ProtectedRoute redirect.

## Shared Components
- backend/app/extensions.py - singletons db, migrate, bcrypt, jwt, cors imported everywhere (prevents circular imports).
- backend/app/__init__.py - create_app(config_name) registers extensions, blueprints and error handlers; wsgi.py exposes app for gunicorn.
- backend/app/utils/responses.py - success(data, status) and error_response(code, message, status, fields) builders used by all endpoints.
- backend/app/utils/errors.py - ApiError class plus register_error_handlers(app).
- backend/app/utils/validators.py - shared email/username/password rules and PASSWORD_RULES constant.
- backend/app/models/user.py - User model and password helpers, the only place bcrypt is called.
- frontend/src/api/client.js - axios instance with baseURL from VITE_API_BASE_URL, request interceptor adding Bearer token, response interceptor normalising the error envelope and clearing auth on 401.
- frontend/src/context/AuthContext.jsx - AuthProvider + useAuth hook holding user/token, login/register/logout, token persisted in localStorage key 'auth_token'.
- frontend/src/components/Layout.jsx + Navbar.jsx - MUI AppBar with Tailwind responsive classes, Drawer menu under md breakpoint, links Home/About Us/Contact Us plus Login/Register or Logout.
- frontend/src/components/ProtectedRoute.jsx - wraps /dashboard, redirects to / when no valid token.
- frontend/src/components/Alert.jsx - MUI Alert wrapper rendering API error messages and field errors consistently.
- frontend/src/main.jsx + App.jsx - ThemeProvider, CssBaseline, Tailwind entry index.css, BrowserRouter route table (/, /about, /contact, /register, /dashboard, *).
- docker-compose.yml - services db (postgres:16 with named volume pgdata), backend (gunicorn on 5000, depends_on db healthcheck), frontend (nginx on 80 mapped to 3000); no container_name keys.
