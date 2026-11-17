import asyncio
from datetime import datetime, timezone
from PySide6.QtCore import QThread, Signal
from ..api.client import AlertsClient

class MonitorThread(QThread):
    snapshot = Signal(object)
    failure = Signal(str)
    connection = Signal(bool)

    def __init__(self, token, interval=30, timeout=12, simulation=False, parent=None):
        super().__init__(parent)
        self.token, self.interval, self.timeout = token, max(15, interval), timeout
        self.simulation = simulation
        self._stop = False

    def stop(self):
        self._stop = True
        self.wait(5000)

    def run(self):
        asyncio.run(self._poll())

    async def _poll(self):
        delay = self.interval
        sim_step = 0
        while not self._stop:
            try:
                if self.simulation:
                    from ..api.models import Alert
                    from ..config import REGIONS
                    demo = REGIONS[9]
                    scenarios = [(), (Alert("demo-drone",demo[0],demo[1],datetime.now(timezone.utc).isoformat(),"air_raid","yellow",({"threat_type":"drones","level":"yellow"},),{}),),
                                 (Alert("demo-missile",demo[0],demo[1],datetime.now(timezone.utc).isoformat(),"air_raid","red",({"threat_type":"missiles","level":"red"},),{}),),
                                 (Alert("demo-unknown",demo[0],demo[1],datetime.now(timezone.utc).isoformat(),"air_raid","red",(),{}),)]
                    if sim_step % 5 == 4:
                        self.connection.emit(False); self.failure.emit("ІМІТАЦІЯ: збій з’єднання"); sim_step += 1
                        await asyncio.sleep(min(delay, 3)); continue
                    alerts = scenarios[sim_step % len(scenarios)]; sim_step += 1
                    delay = 3
                else:
                    alerts = await AlertsClient(self.token, self.timeout).fetch_active()
                self.snapshot.emit((alerts, datetime.now(timezone.utc)))
                self.connection.emit(True)
                delay = self.interval
            except Exception as exc:
                self.connection.emit(False)
                self.failure.emit(str(exc))
                delay = min(max(delay * 2, self.interval), 300)
            for _ in range(delay):
                if self._stop: break
                await asyncio.sleep(1)
