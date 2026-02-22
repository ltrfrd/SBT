from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Driver
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate
from app.utils.auth import hash_password


router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("/", response_model=list[DriverRead])
def list_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).order_by(Driver.id).all()


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return driver


@router.post("/", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    if db.query(Driver).filter(Driver.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    driver = Driver(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        phone=payload.phone,
        is_active=payload.is_active,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(driver_id: int, payload: DriverUpdate, db: Session = Depends(get_db)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)

    if "email" in data:
        exists = db.query(Driver).filter(Driver.email == data["email"], Driver.id != driver_id).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    for key, value in data.items():
        setattr(driver, key, value)

    if password:
        driver.password_hash = hash_password(password)

    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    db.delete(driver)
    db.commit()
