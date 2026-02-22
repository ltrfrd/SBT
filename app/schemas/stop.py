from pydantic import BaseModel, ConfigDict


class StopBase(BaseModel):
    run_id: int
    name: str
    sequence: int
    latitude: float
    longitude: float
    eta_offset_min: int = 0


class StopCreate(StopBase):
    pass


class StopUpdate(BaseModel):
    run_id: int | None = None
    name: str | None = None
    sequence: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    eta_offset_min: int | None = None


class StopRead(StopBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
