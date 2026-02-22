from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Payroll
from app.schemas.payroll import PayrollCreate, PayrollRead, PayrollUpdate


router = APIRouter(prefix="/payrolls", tags=["payrolls"])


@router.get("/", response_model=list[PayrollRead])
def list_payrolls(db: Session = Depends(get_db)):
    return db.query(Payroll).order_by(Payroll.pay_date.desc(), Payroll.id.desc()).all()


@router.get("/{payroll_id}", response_model=PayrollRead)
def get_payroll(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.get(Payroll, payroll_id)
    if not payroll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll entry not found")
    return payroll


@router.post("/", response_model=PayrollRead, status_code=status.HTTP_201_CREATED)
def create_payroll(payload: PayrollCreate, db: Session = Depends(get_db)):
    payroll = Payroll(**payload.model_dump())
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return payroll


@router.put("/{payroll_id}", response_model=PayrollRead)
def update_payroll(payroll_id: int, payload: PayrollUpdate, db: Session = Depends(get_db)):
    payroll = db.get(Payroll, payroll_id)
    if not payroll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll entry not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(payroll, key, value)

    db.commit()
    db.refresh(payroll)
    return payroll


@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payroll(payroll_id: int, db: Session = Depends(get_db)):
    payroll = db.get(Payroll, payroll_id)
    if not payroll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll entry not found")

    db.delete(payroll)
    db.commit()
