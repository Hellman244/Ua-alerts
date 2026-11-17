from datetime import datetime, timezone

class EventManager:
    """Produces one transition per region change; initial fetch only seeds state."""
    def __init__(self, database):
        self.db, self.previous, self.initialized = database, {}, False

    def update(self, alerts):
        current = {a.region_uid: a for a in alerts}
        changes = []
        if self.initialized:
            for uid in self.previous.keys() | current.keys():
                old, new = self.previous.get(uid), current.get(uid)
                old_status = old.classification if old else "SAFE"
                new_status = new.classification if new else "SAFE"
                if old_status != new_status:
                    region = (new or old).region
                    started = new.started_at if new else None
                    key = f"{uid}:{(new.event_id if new else old.event_id)}:{old_status}:{new_status}"
                    now = datetime.now(timezone.utc).isoformat()
                    self.db.record((key, region, old_status, new_status, new_status, started, None if new else now, "alerts.in.ua", now))
                    changes.append((region, old_status, new_status, new))
        self.previous, self.initialized = current, True
        return changes
