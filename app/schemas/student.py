from pydantic import BaseModel, ConfigDict


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    grade: str | None = None
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    dropoff_latitude: float | None = None
    dropoff_longitude: float | None = None
    route_id: int | None = None
    school_id: int | None = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    grade: str | None = None
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    dropoff_latitude: float | None = None
    dropoff_longitude: float | None = None
    route_id: int | None = None
    school_id: int | None = None


class StudentRead(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
