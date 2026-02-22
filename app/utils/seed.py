from sqlalchemy.orm import Session

from app.models import Driver
from app.utils.auth import hash_password


def seed_default_driver(db: Session) -> None:
    existing = db.query(Driver).filter(Driver.email == "driver@sbt.local").first()
    if existing:
        return

    db.add(
        Driver(
            name="Default Driver",
            email="driver@sbt.local",
            password_hash=hash_password("driver123"),
            phone="555-0100",
            is_active=True,
        )
    )
    db.commit()
