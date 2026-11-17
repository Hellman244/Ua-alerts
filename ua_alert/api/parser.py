from .models import Alert

def parse_payload(payload: object) -> tuple[Alert, ...]:
    if not isinstance(payload, dict) or not isinstance(payload.get("alerts"), list):
        raise ValueError("API response does not contain an alerts array")
    parsed = []
    for item in payload["alerts"]:
        if not isinstance(item, dict):
            continue
        title = item.get("location_oblast") or item.get("location_title")
        uid = item.get("location_oblast_uid") or item.get("location_uid")
        if not title or uid is None:
            continue
        threats = item.get("threats", [])
        if not isinstance(threats, list):
            threats = []
        parsed.append(Alert(str(item.get("id") or f"{uid}:{item.get('started_at','')}"), str(uid), str(title),
                            item.get("started_at"), str(item.get("alert_type", "unknown")),
                            item.get("alert_level"), tuple(t for t in threats if isinstance(t, dict)), item))
    return tuple(parsed)
