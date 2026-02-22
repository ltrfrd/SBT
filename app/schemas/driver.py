from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class DriverBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    is_active: bool = True


class DriverCreate(DriverBase):
    password: str


class DriverUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool | None = None
    password: str | None = None


class DriverRead(DriverBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
