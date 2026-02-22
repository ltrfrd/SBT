from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RunBase(BaseModel):
    route_id: int
    driver_id: int
    status: str = "scheduled"


class RunCreate(RunBase):
    pass


class RunUpdate(BaseModel):
    route_id: int | None = None
    driver_id: int | None = None
    status: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None


class RunRead(RunBase):
    id: int
    started_at: datetime | None = None
    ended_at: datetime | None = None
    last_latitude: float | None = None
    last_longitude: float | None = None
    last_updated: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GPSPayload(BaseModel):
    latitude: float
    longitude: float
    speed_kmh: float | None = None
    timestamp: datetime | None = None
