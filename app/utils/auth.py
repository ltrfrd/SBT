import hashlib
import secrets

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Driver


SESSION_DRIVER_KEY = "driver_id"


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    return secrets.compare_digest(check, digest)


def get_current_driver(request: Request, db: Session = Depends(get_db)) -> Driver:
    driver_id = request.session.get(SESSION_DRIVER_KEY)
    if not driver_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    driver = db.get(Driver, driver_id)
    if not driver or not driver.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return driver


def get_current_driver_optional(request: Request, db: Session = Depends(get_db)) -> Driver | None:
    driver_id = request.session.get(SESSION_DRIVER_KEY)
    if not driver_id:
        return None
    return db.get(Driver, driver_id)
