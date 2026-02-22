from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Route, Run, School, Stop
from app.schemas.route import RouteCreate, RouteOut, RouteUpdate


router = APIRouter(prefix="/routes", tags=["routes"])


def _load_route_with_nested(route_id: int, db: Session) -> Route | None:
    stmt = (
        select(Route)
        .where(Route.id == route_id)
        .options(
            joinedload(Route.schools),
            joinedload(Route.runs).joinedload(Run.stops),
        )
    )
    return db.execute(stmt).scalars().unique().first()


def _to_route_out(route: Route) -> RouteOut:
    return RouteOut(
        id=route.id,
        name=route.name,
        code=route.code,
        driver_id=route.driver_id,
        start_latitude=route.start_latitude,
        start_longitude=route.start_longitude,
        end_latitude=route.end_latitude,
        end_longitude=route.end_longitude,
        created_at=route.created_at,
        school_ids=[school.id for school in route.schools],
        runs=sorted(route.runs, key=lambda r: r.id),
    )


@router.get("/", response_model=list[RouteOut])
def list_routes(db: Session = Depends(get_db)):
    stmt = select(Route).options(joinedload(Route.schools), joinedload(Route.runs).joinedload(Run.stops))
    routes = db.execute(stmt).scalars().unique().all()
    return [_to_route_out(route) for route in routes]


@router.get("/{route_id}", response_model=RouteOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = _load_route_with_nested(route_id, db)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return _to_route_out(route)


@router.post("/", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
def create_route(payload: RouteCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    school_ids = data.pop("school_ids", [])
    runs_payload = data.pop("runs", [])

    try:
        route = Route(**data)
        db.add(route)
        db.flush()

        if school_ids:
            schools = db.query(School).filter(School.id.in_(school_ids)).all()
            route.schools = schools

        for run_payload in runs_payload:
            stops_payload = run_payload.pop("stops", [])
            run = Run(route_id=route.id, **run_payload)
            db.add(run)
            db.flush()

            for stop_payload in stops_payload:
                stop = Stop(run_id=run.id, **stop_payload)
                db.add(stop)

        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create route with nested runs/stops: {exc}",
        ) from exc

    route = _load_route_with_nested(route.id, db)
    return _to_route_out(route)


@router.put("/{route_id}", response_model=RouteOut)
def update_route(route_id: int, payload: RouteUpdate, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    data = payload.model_dump(exclude_unset=True)
    school_ids = data.pop("school_ids", None)

    for key, value in data.items():
        setattr(route, key, value)

    if school_ids is not None:
        schools = db.query(School).filter(School.id.in_(school_ids)).all() if school_ids else []
        route.schools = schools

    db.commit()
    route = _load_route_with_nested(route_id, db)
    return _to_route_out(route)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    route = db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    db.delete(route)
    db.commit()
