from pydantic import BaseModel, ConfigDict


class SchoolBase(BaseModel):
    name: str
    address: str
    latitude: float | None = None
    longitude: float | None = None


class SchoolCreate(SchoolBase):
    pass


class SchoolUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SchoolRead(SchoolBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
