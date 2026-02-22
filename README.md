# School Bus Tracking System (SBT) - FastAPI Backend

## Stack
- FastAPI
- SQLAlchemy ORM + SQLite
- Jinja2 templates
- Bootstrap 5
- Leaflet maps
- Session-based driver authentication
- WebSocket GPS streaming

## Project Structure
- `app/models` SQLAlchemy models and relationships
- `app/schemas` Pydantic request/response schemas
- `app/routers` modular API/UI routers
- `app/utils` auth, GPS business logic, websocket manager, seed helpers
- `app/templates` Jinja2 HTML templates

## Quick Start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
- Dashboard: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login`
- API docs: `http://127.0.0.1:8000/docs`

Demo login:
- Email: `driver@sbt.local`
- Password: `driver123`

## Key Features
- CRUD APIs for Driver, School, Student, Route, Stop, Run, Payroll.
- Route-to-School many-to-many and Route-to-Stops/Students one-to-many relationships.
- Driver session login/logout with protected CRUD APIs.
- Dashboard with operational counts and report snippets.
- Driver run page with live GPS stream over `/runs/ws/gps/{run_id}`.
- GPS business logic in `app/utils/gps.py`:
  - coordinate validation
  - nearest stop lookup
  - route progress estimation
  - ETA calculation
  - approaching-stop alerting
