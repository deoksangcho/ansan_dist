import json
from datetime import datetime
from pathlib import Path


FREE_QUOTAS = {
    "geocoding": 20000,
    "routing": 1000,
}


class UsageService:
    def __init__(self, usage_path: Path) -> None:
        self.usage_path = usage_path

    def _today_key(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def load(self) -> dict:
        if not self.usage_path.exists():
            return {}

        try:
            return json.loads(self.usage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self, data: dict) -> None:
        self.usage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def increment(self, metric: str, count: int = 1) -> None:
        data = self.load()
        today_key = self._today_key()
        today_usage = data.get(today_key, {"geocoding": 0, "routing": 0})
        today_usage[metric] = int(today_usage.get(metric, 0)) + count
        data[today_key] = today_usage
        self.save(data)

    def today_usage(self) -> dict:
        data = self.load()
        today_usage = data.get(self._today_key(), {"geocoding": 0, "routing": 0})

        return {
            "date": self._today_key(),
            "geocoding_used": int(today_usage.get("geocoding", 0)),
            "routing_used": int(today_usage.get("routing", 0)),
            "geocoding_limit": FREE_QUOTAS["geocoding"],
            "routing_limit": FREE_QUOTAS["routing"],
        }
