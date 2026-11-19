# Build Plan

## Phase 1: Phase 1 - Foundation: Repo, Backend Core, Database & Docker

Goal: A reviewer can start the stack with Docker Compose and get a running Flask API backed by PostgreSQL 16, with migrations applied, a working /api/v1/health endpoint, the shared error/response/validation utilities and the User table in place.

- **1.1 Repository scaffold and root configuration** (stories: S339 1. Initialize Monorepo and Docker Compose Environment)
  Create the monorepo skeleton: backend/, frontend/ (empty placeholder for now), docs/ with architecture.md copied from the architecture description, Readme.md with setup/run instructions, root .env.example (POSTGRES_* , DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY, FRONTEND_ORIGIN, VITE_API_BASE_URL) and .gitignore for Python, Node and env files. No application code yet.
- **1.2 Flask application factory, extensions and config** (stories: S339 1. Initialize Monorepo and Docker Compose Environment)
  Build backend/requirements.txt (Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt, Flask-JWT-Extended, Flask-Cors, email-validator, python-dotenv, gunicorn, psycopg2-binary, pytest, pytest-flask), backend/wsgi.py exposing app for gunicorn, backend/app/__init__.py with create_app(config_name) registering extensions, blueprints and error handlers, backend/app/extensions.py with db/migrate/bcrypt/jwt/cors singletons, backend/app/config.py with Development/Production/Testing classes reading DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FRONTEND_ORIGIN from the environment (Testing uses SQLite in-memory), CORS bound to FRONTEND_ORIGIN, app.logger StreamHandler setup (DEBUG dev / INFO prod), and backend/app/api/health.py exposing GET /api/v1/health.
- **1.3 Shared backend utilities: errors, responses, validators**
  Implement backend/app/utils/errors.py (ApiError(code, message, status, fields) plus register_error_handlers(app) converting ApiError, HTTPException and unhandled Exception into the error envelope with codes VALIDATION_ERROR, NOT_FOUND, INTERNAL_ERROR), backend/app/utils/responses.py (success(data, status) and error_response(code, message, status, fields) builders) and backend/app/utils/validators.py (validate_email_format using email-validator, validate_username, validate_password with the shared PASSWORD_RULES constant: >=8 chars, >=1 uppercase, >=1 digit, >=1 special from !@#$%^&*()-_=+[]{};:,.<>?/|~, one message per failed rule). Wire register_error_handlers into create_app.
- **1.4 User model and Flask-Migrate migrations** (stories: S340 2. Configure PostgreSQL Database and SQLAlchemy ORM)
  Add backend/app/models/user.py with the User entity (table 'users': id Integer PK, username String(50) unique not null, email String(255) unique lowercased not null, password_hash String(255) not null, created_at/updated_at UTC datetimes) plus set_password/check_password using Flask-Bcrypt (the only place bcrypt is called) and to_dict() returning id, username, email, created_at only. Initialise Flask-Migrate under backend/migrations/ and generate the initial migration creating the users table with its unique constraints and a case-insensitive lookup strategy via func.lower.
- **1.5 Backend test harness**
  Add backend/pytest.ini and backend/tests/conftest.py creating an app fixture with TestingConfig (SQLite in-memory), a client fixture and a db fixture with per-test teardown. Add backend/tests/test_validators.py covering email/username/password rules and a health endpoint test asserting the success envelope.
- **1.6 Backend Dockerfile and Docker Compose with PostgreSQL** (stories: S339 1. Initialize Monorepo and Docker Compose Environment, S340 2. Configure PostgreSQL Database and SQLAlchemy ORM)
  Create backend/Dockerfile (python:3.11-slim, install requirements, run gunicorn on 5000) and backend/.env.example. Create root docker-compose.yml with services db (postgres:16, named volume pgdata, healthcheck), backend (depends_on db healthcheck, env from .env, port 5000) and no container_name keys. Document how to run migrations inside the backend container in Readme.md.

Done when:
- `docker compose up --build` starts db and backend services successfully (no container_name keys used).
- GET /api/v1/health returns 200 with a {"data": {...}} envelope.
- `flask db upgrade` creates the 'users' table with id, username, email, password_hash, created_at, updated_at.
- Unknown routes and raised ApiError instances return the documented error envelope with correct status codes.
- pytest suite runs green against the SQLite in-memory TestingConfig.
- No secrets are committed; .env.example files list DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY, FRONTEND_ORIGIN.

## Phase 2: Phase 2 - Authentication API

Goal: A reviewer can register a user, log in with username or email and fetch the current user with a Bearer token, all with server-side validation, bcrypt hashing and the documented error envelope.

- **2.1 Auth request schemas and registration endpoint** (stories: S343 1. User Registration Interface and Backend Model, S344 2. Email Format and Password Security Validation, S345 3. Secure Password Storage with Hashing)
  Add backend/app/schemas/auth_schemas.py with parse/validate helpers for the register and login payloads (flat JSON objects) raising ApiError(VALIDATION_ERROR, 400, fields) via utils/validators.py. Add backend/app/api/auth.py blueprint registered at /api/v1/auth with POST /register: validate email/username/password, normalise email to lowercase, persist the User with set_password, return 201 {"data": user.to_dict()}. Route body only parses input, calls the model and returns the envelope.
- **2.2 Duplicate detection and registration error handling** (stories: S343 1. User Registration Interface and Backend Model, S344 2. Email Format and Password Security Validation)
  Extend the register endpoint to detect existing accounts case-insensitively (func.lower on username and email) and raise ApiError with 409 DUPLICATE_USERNAME or DUPLICATE_EMAIL, plus a defensive IntegrityError fallback. Log registration outcomes with username only through app.logger.
- **2.3 Login endpoint with JWT issuance** (stories: S346 1. User Login with Username or Email and JWT Authentication)
  Add POST /api/v1/auth/login to backend/app/api/auth.py: accept {identifier, password}, look up the user by lowercased email or by username (case-insensitive), verify with check_password, and on success return 200 {"data": {access_token, user}} using Flask-JWT-Extended with 1 hour expiry and identity str(user.id). All failures return 401 INVALID_CREDENTIALS with the message "Invalid username/email or password". Log login outcomes with username only.
- **2.4 Protected /auth/me endpoint and JWT error envelope** (stories: S346 1. User Login with Username or Email and JWT Authentication, S347 2. Protected User Dashboard)
  Add GET /api/v1/auth/me guarded by @jwt_required() returning the current user via to_dict(), 404 NOT_FOUND if the identity no longer resolves. Register Flask-JWT-Extended error loaders (unauthorized, invalid_token, expired_token, revoked) so missing/invalid tokens produce 401 TOKEN_MISSING / TOKEN_INVALID in the standard error envelope.
- **2.5 Backend auth test suite** (stories: S343 1. User Registration Interface and Backend Model, S344 2. Email Format and Password Security Validation, S345 3. Secure Password Storage with Hashing, S346 1. User Login with Username or Email and JWT Authentication)
  Add backend/tests/test_auth.py covering: successful registration persists a hashed (non-plaintext) password, invalid email and each failing password rule return 400 with field messages, duplicate username and duplicate email return 409, login succeeds by username and by email, wrong password returns the generic 401, and /api/v1/auth/me without a token or with a malformed token returns 401.

Done when:
- POST /api/v1/auth/register returns 201 with the user object and rejects bad email/weak password with 400 VALIDATION_ERROR including per-rule messages in error.fields.password.
- Duplicate username/email return 409 DUPLICATE_USERNAME / DUPLICATE_EMAIL (case-insensitive).
- POST /api/v1/auth/login accepts an 'identifier' matching email or username, returns 200 with access_token (1h, identity = str(user.id)) and user; failures return 401 INVALID_CREDENTIALS with the generic message.
- GET /api/v1/auth/me returns the user with a valid token and 401 TOKEN_MISSING / TOKEN_INVALID otherwise.
- password_hash never appears in any response; logs contain usernames only.
- pytest suite (validation, duplicate signup, login by username and email, protected route without token) passes.

## Phase 3: Phase 3 - Frontend Shell: Responsive Layout and Public Pages

Goal: A user can open the SPA in the browser (via Docker Compose or Vite dev) and navigate between Home, About Us and Contact Us with a responsive MUI/Tailwind navbar that collapses to a drawer on mobile; the axios client and auth context plumbing exist.

- **3.1 Vite React 19 scaffold with Tailwind and MUI** (stories: S339 1. Initialize Monorepo and Docker Compose Environment, S341 1. Responsive Layout and Public Navigation Menu)
  Create frontend/ with Vite 5 + React 19 (JavaScript), package.json scripts, vite.config.js (dev proxy/port), tailwind.config.js + postcss config, index.html, src/index.css (Tailwind entry), src/main.jsx with MUI ThemeProvider, CssBaseline and BrowserRouter, and src/App.jsx holding the route table placeholders for /, /about, /contact, /register, /dashboard and *. Add frontend/.env.example with VITE_API_BASE_URL.
- **3.2 Responsive Layout and Navbar** (stories: S341 1. Responsive Layout and Public Navigation Menu)
  Build frontend/src/components/Layout.jsx (page shell wrapping an Outlet with container spacing) and Navbar.jsx using an MUI AppBar with Tailwind responsive utilities: inline links Home / About Us / Contact Us plus auth actions at md and above, Drawer menu below md, React Router Links for navigation. Auth actions render Login/Register or Logout based on a context value (placeholder until AuthContext lands).
- **3.3 Public pages: Home, About, Contact, NotFound** (stories: S341 1. Responsive Layout and Public Navigation Menu)
  Create frontend/src/pages/Home.jsx, About.jsx, Contact.jsx and NotFound.jsx with responsive MUI/Tailwind content, and wire them into the App.jsx route table inside Layout. Home holds a placeholder slot where the login form and registration access will be added in the next phase.
- **3.4 Axios client and auth API module**
  Implement frontend/src/api/client.js: an axios instance with baseURL from VITE_API_BASE_URL, a request interceptor adding the Bearer token, and a response interceptor normalising the {error:{code,message,fields}} envelope into a consistent shape and clearing stored auth on 401. Add frontend/src/api/auth.js wrapping POST /auth/register, POST /auth/login and GET /auth/me.
- **3.5 AuthContext provider and Alert component**
  Implement frontend/src/context/AuthContext.jsx with AuthProvider + useAuth holding user/token state, login/register/logout actions calling src/api/auth.js, token persisted in localStorage key 'auth_token' and rehydrated on mount via /auth/me. Add frontend/src/components/Alert.jsx, a MUI Alert wrapper rendering an API message plus field errors. Wrap the app in AuthProvider in main.jsx and connect Navbar auth actions to useAuth.
- **3.6 Frontend Dockerfile, nginx and Compose integration** (stories: S339 1. Initialize Monorepo and Docker Compose Environment)
  Add frontend/Dockerfile (node build stage then nginx:alpine serving the dist output) and frontend/nginx.conf with SPA history fallback. Add the frontend service to docker-compose.yml (nginx port 80 mapped to 3000, depends_on backend, no container_name) and update Readme.md with run instructions for the full stack.
- **3.7 Vitest setup and navigation tests** (stories: S341 1. Responsive Layout and Public Navigation Menu)
  Configure Vitest + React Testing Library + jsdom in vite.config.js with a setup file, and add frontend/src/tests specs covering navbar rendering and that clicking Home / About Us / Contact Us renders the corresponding page, plus the NotFound fallback route.

Done when:
- `docker compose up --build` serves the built frontend on port 3000 via nginx alongside backend and db.
- Navigating to /, /about and /contact renders the matching page inside the shared Layout; an unknown path renders NotFound.
- The navbar shows inline links at md and above and a Drawer menu below md.
- axios client attaches a Bearer token from AuthContext and normalises the backend error envelope; a 401 clears stored auth.
- Vitest + RTL navigation tests pass and `npm run build` succeeds with no console errors.

## Phase 4: Phase 4 - Registration, Login and Protected Dashboard

Goal: A visitor can register from the home page, log in with username or email, land on a protected /dashboard showing a personal welcome, and be blocked/redirected when unauthenticated.

- **4.1 Frontend validators mirroring backend rules** (stories: S344 2. Email Format and Password Security Validation)
  Add frontend/src/utils/validators.js with validateEmail, validateUsername and validatePassword mirroring (never replacing) backend/app/utils/validators.py, including the shared password rule set and one message per failed rule, ready for reuse by both forms.
- **4.2 Registration form and Register page** (stories: S343 1. User Registration Interface and Backend Model, S344 2. Email Format and Password Security Validation)
  Build frontend/src/components/RegisterForm.jsx (MUI fields for email, username, password with Tailwind layout, inline client-side validation via utils/validators.js, submit through AuthContext.register -> POST /api/v1/auth/register) and frontend/src/pages/Register.jsx mounting it at /register, rendering server field errors and duplicate email/username conflicts through Alert, and redirecting to the home page or dashboard on success.
- **4.3 Home page login form and registration access** (stories: S342 2. Public Home Page Login and Registration Access, S346 1. User Login with Username or Email and JWT Authentication)
  Build frontend/src/components/LoginForm.jsx (single 'identifier' field plus password, client-side required checks, submit through AuthContext.login -> POST /api/v1/auth/login) and place it on frontend/src/pages/Home.jsx together with a clearly visible link/button to /register. Render the generic invalid-credentials error via Alert and navigate to /dashboard on success.
- **4.4 ProtectedRoute and Dashboard page** (stories: S347 2. Protected User Dashboard)
  Add frontend/src/components/ProtectedRoute.jsx reading token/user from useAuth, showing a loading state while rehydrating and redirecting to / when there is no valid token. Add frontend/src/pages/Dashboard.jsx showing a simple welcome message with the username from GET /api/v1/auth/me, and wrap the /dashboard route with ProtectedRoute in App.jsx. Ensure logout from the Navbar clears the token and returns the user to the home page.
- **4.5 Frontend auth tests** (stories: S344 2. Email Format and Password Security Validation, S346 1. User Login with Username or Email and JWT Authentication, S347 2. Protected User Dashboard)
  Add Vitest + RTL specs in frontend/src/tests covering: RegisterForm rejecting a malformed email and each failing password rule with messages, LoginForm displaying the generic error on a mocked 401, successful login storing the token and redirecting to /dashboard, and ProtectedRoute redirecting to / when no token is present. Mock the axios client in src/api.

Done when:
- The home page shows a login form plus a visible link/button to the registration page.
- Registering with valid details creates the user via POST /api/v1/auth/register and the user can then log in.
- Client-side validation mirrors the backend rules and server-side field errors are rendered through the Alert component.
- Successful login stores the token and redirects to /dashboard, which shows a welcome message with the username.
- Visiting /dashboard without a token redirects to /; logging out clears the token and blocks the dashboard again.
- Vitest tests for form validation and ProtectedRoute redirect pass; backend pytest suite still green; `docker compose up --build` runs the full flow end to end.
