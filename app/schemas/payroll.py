from datetime import date

from pydantic import BaseModel, ConfigDict


class PayrollBase(BaseModel):
    driver_id: int
    run_id: int | None = None
    pay_date: date
    hours_worked: float
    hourly_rate: float
    total_pay: float
    status: str = "pending"


class PayrollCreate(PayrollBase):
    pass


class PayrollUpdate(BaseModel):
    driver_id: int | None = None
    run_id: int | None = None
    pay_date: date | None = None
    hours_worked: float | None = None
    hourly_rate: float | None = None
    total_pay: float | None = None
    status: str | None = None


class PayrollRead(PayrollBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
