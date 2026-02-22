from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StopNestedCreate(BaseModel):
    name: str
    sequence: int
    latitude: float
    longitude: float
    eta_offset_min: int = 0


class StopNestedOut(StopNestedCreate):
    id: int
    run_id: int

    model_config = ConfigDict(from_attributes=True)


class RunNestedCreate(BaseModel):
    driver_id: int
    status: str = "scheduled"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    stops: list[StopNestedCreate] = Field(default_factory=list)


class RunNestedOut(BaseModel):
    id: int
    route_id: int
    driver_id: int
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    last_latitude: float | None = None
    last_longitude: float | None = None
    last_updated: datetime | None = None
    stops: list[StopNestedOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RouteBase(BaseModel):
    name: str
    code: str
    driver_id: int | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    end_latitude: float | None = None
    end_longitude: float | None = None


class RouteCreate(RouteBase):
    school_ids: list[int] = Field(default_factory=list)
    runs: list[RunNestedCreate] = Field(default_factory=list)


class RouteUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    driver_id: int | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    end_latitude: float | None = None
    end_longitude: float | None = None
    school_ids: list[int] | None = None


class RouteOut(RouteBase):
    id: int
    created_at: datetime
    school_ids: list[int] = Field(default_factory=list)
    runs: list[RunNestedOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
