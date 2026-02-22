from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Payroll(Base):
    __tablename__ = "payrolls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False, index=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id"), nullable=True, unique=True)
    pay_date: Mapped[date] = mapped_column(Date, nullable=False)
    hours_worked: Mapped[float] = mapped_column(Float, nullable=False)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False)
    total_pay: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    driver = relationship("Driver", back_populates="payrolls")
    run = relationship("Run", back_populates="payroll")
