from app.schemas.auth import LoginRequest
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate
from app.schemas.payroll import PayrollCreate, PayrollRead, PayrollUpdate
from app.schemas.route import RouteCreate, RouteOut, RouteUpdate
from app.schemas.run import GPSPayload, RunCreate, RunRead, RunUpdate
from app.schemas.school import SchoolCreate, SchoolRead, SchoolUpdate
from app.schemas.stop import StopCreate, StopRead, StopUpdate
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate

__all__ = [
    "LoginRequest",
    "DriverCreate",
    "DriverRead",
    "DriverUpdate",
    "SchoolCreate",
    "SchoolRead",
    "SchoolUpdate",
    "StudentCreate",
    "StudentRead",
    "StudentUpdate",
    "RouteCreate",
    "RouteOut",
    "RouteUpdate",
    "StopCreate",
    "StopRead",
    "StopUpdate",
    "RunCreate",
    "RunRead",
    "RunUpdate",
    "GPSPayload",
    "PayrollCreate",
    "PayrollRead",
    "PayrollUpdate",
]
