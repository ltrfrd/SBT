from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401 - imported for metadata registration
from app.routers import auth, dashboard, driver, payroll, route, run, school, stop, student
from app.utils.auth import get_current_driver
from app.utils.seed import seed_default_driver
from app.utils.ws_manager import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_driver(db)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.templates = Jinja2Templates(directory="app/templates")
app.state.ws_manager = ConnectionManager()

app.mount("/static", StaticFiles(directory="app/templates"), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)

protected = [Depends(get_current_driver)]
app.include_router(driver.router, dependencies=protected)
app.include_router(school.router, dependencies=protected)
app.include_router(student.router, dependencies=protected)
app.include_router(route.router, dependencies=protected)
app.include_router(stop.router, dependencies=protected)
app.include_router(run.router)
app.include_router(run.ws_router)
app.include_router(payroll.router, dependencies=protected)


@app.get("/health")
def health():
    return {"status": "ok"}
