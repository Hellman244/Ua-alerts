import aiohttp
from .parser import parse_payload

class AlertsClient:
    def __init__(self, token: str = "", timeout: int = 12):
        self.token, self.timeout = token.strip(), timeout

    async def fetch_active(self):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get("https://api.alerts.in.ua/v1/alerts/active.json") as response:
                response.raise_for_status()
                return parse_payload(await response.json(content_type=None))
