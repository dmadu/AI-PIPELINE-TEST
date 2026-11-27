# Build Plan

## Phase 1: Phase 1: Project Scaffolding, Database Setup & Core Shared Architecture

Goal: The application repository is initialized with a working Flask backend, PostgreSQL database connection, user model, Alembic migrations, and a React 19 frontend with Tailwind, MUI, and routing configured.

- **1.1 Initialize Backend Project Structure and Configuration**
  Set up backend/app/ directory, application factory in backend/app/__init__.py, configuration in backend/app/config.py, environment variables, PostgreSQL connection URI, and Gunicorn setup.
- **1.2 Implement User Database Model and Flask-Migrate**
  Create backend/app/models/user.py with the User model (id, email, username, password_hash, created_at) and set up Flask-Migrate for database migrations.
- **1.3 Initialize Frontend Project Structure and Styling**
  Set up frontend/ directory with React 19, Tailwind CSS v3, Material UI v6, React Router DOM v6, and base HTML/CSS configuration ensuring no style clashes.
- **1.4 Implement Frontend API Client and Auth Context**
  Create frontend/src/services/api.js with Axios client and request interceptors for JWT injection, and create frontend/src/context/AuthContext.js for authentication state management.

Done when:
- Flask backend boots successfully with SQLAlchemy and Flask-Migrate configured
- PostgreSQL 16 connection established and user database model defined
- React 19 frontend boots with Tailwind CSS and Material UI v6 integrated
- Axios client and AuthContext shared structure established

## Phase 2: Phase 2: Public Layout, Navigation & Static Pages

Goal: Users can view the responsive application layout across devices and navigate between Home, About Us, and Contact Us pages.

- **2.1 Implement Responsive Application Layout and Navigation** (stories: S1 1. Initialize Project Repository and Technical Stack, S2 1. Responsive Application Layout Setup)
  Create frontend/src/components/Layout.js providing a responsive navigation bar and main wrapper layout using Tailwind CSS and Material UI.
- **2.2 Implement Static About Us and Contact Us Pages** (stories: S3 2. Public Home Page Navigation Menu)
  Create static page views in frontend/src/pages/ for About and Contact, and configure React Router DOM routes in the main application entry point.

Done when:
- Responsive navigation bar and layout wrapper render correctly across desktop, tablet, and mobile viewports
- React Router DOM correctly handles navigation between Home, About Us, and Contact Us pages

## Phase 3: Phase 3: User Registration & Security Backend

Goal: New users can be registered via the API with secure server-side email validation, password policy enforcement, and bcrypt password hashing stored in PostgreSQL.

- **3.1 Implement Password Validation and Hashing Services** (stories: S6 2. Email Format Validation, S7 3. Password Security Requirements, S8 4. Secure Password Storage with Hashing)
  Create backend/app/services/auth_service.py with validation logic for email format and password policy requirements, and integrate Flask-Bcrypt for secure password hashing.
- **3.2 Implement User Registration API Endpoint** (stories: S5 1. User Registration Form and Details, S6 2. Email Format Validation, S7 3. Password Security Requirements, S8 4. Secure Password Storage with Hashing)
  Create backend/app/routes/auth_routes.py with the POST /api/auth/register endpoint handling incoming JSON payloads, validation, database persistence, and proper error/success response codes.

Done when:
- Backend registration endpoint /api/auth/register handles user creation
- Server-side validation enforces email format and password strength requirements (min 8 chars, 1 uppercase, 1 digit, 1 special char)
- Passwords are securely hashed using Flask-Bcrypt before database persistence

## Phase 4: Phase 4: User Registration Frontend & Public Home Page

Goal: Visitors can access the home page containing login form access, user registration view with real-time validation, and account creation.

- **4.1 Implement Home Page Login Form Access and Layout** (stories: S3 2. Public Home Page Navigation Menu, S4 3. Home Page Login Form and Registration Access)
  Create frontend/src/pages/Home.js featuring a login form preview and navigation link/button to the user registration view.
- **4.2 Implement User Registration View and Form Validation** (stories: S5 1. User Registration Form and Details, S6 2. Email Format Validation, S7 3. Password Security Requirements)
  Create frontend/src/pages/Register.js with input fields for email, username, and password, mirroring backend email format and password security validation rules with error banners.

Done when:
- Home page renders login form container and link to user registration
- Registration form captures email, username, and password with frontend validation matching backend policy
- Successful registration submits to backend and provides user feedback

## Phase 5: Phase 5: Authentication & Protected Dashboard

Goal: Users can log in flexibly using either username or email with password, receive a JWT token, and access a protected user dashboard with automatic redirection.

- **5.1 Implement Flexible Backend Login and JWT Generation** (stories: S9 1. Flexible User Authentication)
  Add POST /api/auth/login endpoint in backend/app/routes/auth_routes.py supporting authentication via username or email with password verification, issuing JWT tokens via Flask-JWT-Extended.
- **5.2 Implement Protected Route Wrapper Component** (stories: S10 2. Protected Dashboard Access and Welcome Message)
  Create frontend/src/components/ProtectedRoute.js verifying authentication state via AuthContext and redirecting unauthenticated users to the login view.
- **5.3 Implement Login Page and Protected Dashboard View** (stories: S9 1. Flexible User Authentication, S10 2. Protected Dashboard Access and Welcome Message)
  Create frontend/src/pages/Login.js for user login supporting flexible username/email entry, and frontend/src/pages/Dashboard.js displaying a simple welcome message wrapped with ProtectedRoute.

Done when:
- Backend login endpoint /api/auth/login authenticates via username or email and returns a JWT token via Flask-JWT-Extended
- Frontend login form handles flexible authentication and stores token via AuthContext
- Protected dashboard route verifies JWT tokens and redirects unauthenticated users to login
- Dashboard displays a simple welcome message for authenticated users
