from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "School Bus Tracking System")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./sbt.db")
    default_speed_kmh: float = float(os.getenv("DEFAULT_SPEED_KMH", "25"))
    alert_threshold_meters: float = float(os.getenv("ALERT_THRESHOLD_METERS", "250"))


settings = Settings()
