# Project Setup & Architecture

This repository is initialized with Docker and Docker Compose configured for Flask, React 19, and PostgreSQL 16.

## Directory Structure

- `frontend/`: React 19 application
- `backend/`: Flask application
- `database/`: Database initialization scripts and migrations
- `docker/`: Dockerfiles and container-specific configurations
- `tests/`: Integration and end-to-end test suites

## Running the Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Build and start containers using Docker Compose:
   ```bash
   docker compose up --build
   ```

3. Access the services:
   - Frontend (React 19): http://localhost:3000
   - Backend (Flask): http://localhost:5000
   - PostgreSQL 16: localhost:5432
