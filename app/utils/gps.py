import math
from collections.abc import Sequence
from datetime import datetime, timezone

from app.config import settings


def validate_gps(latitude: float, longitude: float) -> bool:
    return -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def compute_nearest_stop(latitude: float, longitude: float, stops: Sequence) -> tuple[object | None, float, int]:
    if not stops:
        return None, float("inf"), -1

    best_stop = None
    best_distance = float("inf")
    best_index = -1

    for index, stop in enumerate(stops):
        dist = haversine_meters(latitude, longitude, stop.latitude, stop.longitude)
        if dist < best_distance:
            best_stop = stop
            best_distance = dist
            best_index = index

    return best_stop, best_distance, best_index


def get_ordered_run_stops(run: object) -> list[object]:
    return sorted(getattr(run, "stops", []) or [], key=lambda s: s.sequence)


def calculate_route_progress(current_stop_index: int, total_stops: int, distance_to_current_m: float) -> float:
    if total_stops <= 0:
        return 0.0
    if total_stops == 1:
        return 100.0

    base_progress = (current_stop_index / (total_stops - 1)) * 100
    proximity_boost = max(0.0, min(5.0, (1 - (distance_to_current_m / 200)) * 5))
    return max(0.0, min(100.0, base_progress + proximity_boost))


def estimate_eta_minutes(distance_m: float, speed_kmh: float | None) -> int:
    speed = speed_kmh if speed_kmh and speed_kmh > 0 else settings.default_speed_kmh
    speed_mps = (speed * 1000) / 3600
    return max(0, int(distance_m / speed_mps / 60))


def trigger_approaching_alert(distance_to_next_stop_m: float, next_stop_name: str | None) -> str | None:
    if next_stop_name and distance_to_next_stop_m <= settings.alert_threshold_meters:
        return f"Approaching {next_stop_name}"
    return None


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)
