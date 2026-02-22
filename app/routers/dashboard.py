from sqlalchemy import func
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Driver, Payroll, Route, Run, School, Stop, Student
from app.utils.auth import get_current_driver_optional


router = APIRouter(tags=["dashboard"])


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db), current_driver: Driver | None = Depends(get_current_driver_optional)):
    if not current_driver:
        return RedirectResponse(url="/login", status_code=303)

    metrics = {
        "drivers": db.query(func.count(Driver.id)).scalar() or 0,
        "schools": db.query(func.count(School.id)).scalar() or 0,
        "students": db.query(func.count(Student.id)).scalar() or 0,
        "routes": db.query(func.count(Route.id)).scalar() or 0,
        "stops": db.query(func.count(Stop.id)).scalar() or 0,
        "runs": db.query(func.count(Run.id)).scalar() or 0,
        "active_runs": db.query(func.count(Run.id)).filter(Run.status == "active").scalar() or 0,
        "pending_payrolls": db.query(func.count(Payroll.id)).filter(Payroll.status == "pending").scalar() or 0,
    }

    route_load = (
        db.query(Route.name, func.count(Student.id).label("student_count"))
        .outerjoin(Student, Student.route_id == Route.id)
        .group_by(Route.id)
        .order_by(func.count(Student.id).desc())
        .limit(5)
        .all()
    )

    recent_runs = db.query(Run).order_by(Run.id.desc()).limit(8).all()

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "driver": current_driver,
            "metrics": metrics,
            "route_load": route_load,
            "recent_runs": recent_runs,
        },
    )
