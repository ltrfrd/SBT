from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Driver
from app.utils.auth import SESSION_DRIVER_KEY, get_current_driver, verify_password


router = APIRouter(tags=["auth"])


@router.get("/login")
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.email == email).first()
    if not driver or not verify_password(password, driver.password_hash):
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=400,
        )

    request.session[SESSION_DRIVER_KEY] = driver.id
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@router.get("/auth/me")
def me(driver: Driver = Depends(get_current_driver)):
    return JSONResponse({"id": driver.id, "name": driver.name, "email": driver.email})
