from dataclasses import dataclass

@dataclass
class RegionState:
    status: str = "UNKNOWN"
    active: bool = False
    alert: object = None

def classify(alert):
    return alert.classification if alert else "SAFE"
