
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import Driver, Run
from app.schemas.run import RunCreate, RunRead, RunUpdate
from app.utils.auth import SESSION_DRIVER_KEY, get_current_driver, get_current_driver_optional
from app.utils.gps import (
    calculate_route_progress,
    compute_nearest_stop,
    estimate_eta_minutes,
    get_ordered_run_stops,
    haversine_meters,
    trigger_approaching_alert,
    utc_now,
    validate_gps,
)


router = APIRouter(prefix="/runs", tags=["runs"])
ws_router = APIRouter(tags=["runs"])


@router.get("/", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db), _: Driver = Depends(get_current_driver)):
    return db.query(Run).order_by(Run.id.desc()).all()


@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id: int, db: Session = Depends(get_db), _: Driver = Depends(get_current_driver)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.post("/", response_model=RunRead, status_code=status.HTTP_201_CREATED)
def create_run(payload: RunCreate, db: Session = Depends(get_db), _: Driver = Depends(get_current_driver)):
    run = Run(**payload.model_dump())
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.put("/{run_id}", response_model=RunRead)
def update_run(run_id: int, payload: RunUpdate, db: Session = Depends(get_db), _: Driver = Depends(get_current_driver)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(run, key, value)

    db.commit()
    db.refresh(run)
    return run


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_run(run_id: int, db: Session = Depends(get_db), _: Driver = Depends(get_current_driver)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    db.delete(run)
    db.commit()


@router.post("/{run_id}/start", response_model=RunRead)
def start_run(run_id: int, db: Session = Depends(get_db), driver: Driver = Depends(get_current_driver)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.driver_id != driver.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Run not assigned to current driver")

    run.status = "active"
    if not run.started_at:
        run.started_at = datetime.utcnow()
    run.ended_at = None
    db.commit()
    db.refresh(run)
    return run


@router.post("/{run_id}/finish", response_model=RunRead)
def finish_run(run_id: int, db: Session = Depends(get_db), driver: Driver = Depends(get_current_driver)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.driver_id != driver.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Run not assigned to current driver")

    run.status = "completed"
    run.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(run)
    return run


@router.get("/{run_id}/driver")
def driver_run_page(
    run_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_driver: Driver | None = Depends(get_current_driver_optional),
):
    if not current_driver:
        return RedirectResponse(url="/login", status_code=303)

    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.driver_id != current_driver.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Run not assigned to current driver")

    db.refresh(run)
    stops = get_ordered_run_stops(run)

    return request.app.state.templates.TemplateResponse(
        "run_driver.html",
        {
            "request": request,
            "driver": current_driver,
            "run": run,
            "route": run.route,
            "stops": stops,
        },
    )


@ws_router.websocket("/ws/gps/{run_id}")
async def gps_socket(websocket: WebSocket, run_id: int):
    driver_id = websocket.session.get(SESSION_DRIVER_KEY)
    if not driver_id:
        await websocket.close(code=4401)
        return

    manager = websocket.app.state.ws_manager
    await manager.connect(run_id, websocket)

    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run or run.driver_id != driver_id:
            await websocket.send_json({"error": "Not authorized for this run"})
            await websocket.close(code=4403)
            manager.disconnect(run_id, websocket)
            return

        while True:
            payload = await websocket.receive_json()
            lat = payload.get("latitude")
            lon = payload.get("longitude")
            speed_kmh = payload.get("speed_kmh")

            if lat is None or lon is None or not validate_gps(lat, lon):
                await websocket.send_json({"error": "Invalid GPS coordinates"})
                continue

            run = db.get(Run, run_id)
            if not run:
                await websocket.send_json({"error": "Run not found"})
                continue
            if run.status != "active":
                await websocket.send_json({"error": "Run is not active"})
                continue

            stops = get_ordered_run_stops(run)

            nearest_stop, dist_to_current, current_index = compute_nearest_stop(lat, lon, stops)
            next_stop = stops[current_index + 1] if current_index >= 0 and current_index < len(stops) - 1 else None
            dist_to_next = haversine_meters(lat, lon, next_stop.latitude, next_stop.longitude) if next_stop else 0

            progress = calculate_route_progress(max(current_index, 0), len(stops), dist_to_current)
            eta_minutes = estimate_eta_minutes(dist_to_next, speed_kmh)
            alert = trigger_approaching_alert(dist_to_next, next_stop.name if next_stop else None)

            run.last_latitude = lat
            run.last_longitude = lon
            run.last_updated = datetime.utcnow()
            db.commit()

            update = {
                "run_id": run_id,
                "timestamp": utc_now().isoformat(),
                "latitude": lat,
                "longitude": lon,
                "current_stop": nearest_stop.name if nearest_stop else None,
                "next_stop": next_stop.name if next_stop else None,
                "progress_percent": round(progress, 2),
                "eta_minutes": eta_minutes,
                "distance_to_next_m": round(dist_to_next, 2),
                "alert": alert,
            }

            await manager.broadcast(run_id, update)
    except WebSocketDisconnect:
        manager.disconnect(run_id, websocket)
    finally:
        manager.disconnect(run_id, websocket)
        db.close()
