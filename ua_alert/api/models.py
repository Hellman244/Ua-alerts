from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Alert:
    event_id: str
    region_uid: str
    region: str
    started_at: str | None
    alert_type: str
    alert_level: str | None
    threats: tuple[dict, ...]
    raw: dict

    @property
    def threat_types(self) -> tuple[str, ...]:
        return tuple(str(t.get("threat_type", "unknown")).lower() for t in self.threats)

    @property
    def classification(self) -> str:
        kinds = set(self.threat_types)
        if kinds & {"drones", "uav", "shahed", "drone"}:
            return "DRONE DANGER"
        if kinds & {"missiles", "missile", "bombing", "guided_bombs", "kab"}:
            return "MISSILE / BOMBING DANGER"
        return "AIR RAID ALERT — TYPE UNKNOWN"

@dataclass(frozen=True)
class Snapshot:
    alerts: tuple[Alert, ...]
    received_at: datetime
