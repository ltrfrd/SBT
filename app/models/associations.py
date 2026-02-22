from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base


route_school_association = Table(
    "route_school_association",
    Base.metadata,
    Column("route_id", Integer, ForeignKey("routes.id", ondelete="CASCADE"), primary_key=True),
    Column("school_id", Integer, ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True),
)
