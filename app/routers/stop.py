from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stop
from app.schemas.stop import StopCreate, StopRead, StopUpdate


router = APIRouter(prefix="/stops", tags=["stops"])


@router.get("/", response_model=list[StopRead])
def list_stops(db: Session = Depends(get_db)):
    return db.query(Stop).order_by(Stop.run_id, Stop.sequence).all()


@router.get("/{stop_id}", response_model=StopRead)
def get_stop(stop_id: int, db: Session = Depends(get_db)):
    stop = db.get(Stop, stop_id)
    if not stop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    return stop


@router.post("/", response_model=StopRead, status_code=status.HTTP_201_CREATED)
def create_stop(payload: StopCreate, db: Session = Depends(get_db)):
    stop = Stop(**payload.model_dump())
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop


@router.put("/{stop_id}", response_model=StopRead)
def update_stop(stop_id: int, payload: StopUpdate, db: Session = Depends(get_db)):
    stop = db.get(Stop, stop_id)
    if not stop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(stop, key, value)

    db.commit()
    db.refresh(stop)
    return stop


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: int, db: Session = Depends(get_db)):
    stop = db.get(Stop, stop_id)
    if not stop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")

    db.delete(stop)
    db.commit()
