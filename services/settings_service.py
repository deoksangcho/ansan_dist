import json
from pathlib import Path


DEFAULT_SETTINGS = {
    "default_start_column": "출발지",
    "default_end_column": "도착지",
    "default_result_column": "도보거리_km",
    "tmap_app_key": "",
}


class SettingsService:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def load(self) -> dict:
        if not self.config_path.exists():
            return DEFAULT_SETTINGS.copy()

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return DEFAULT_SETTINGS.copy()

        settings = DEFAULT_SETTINGS.copy()
        settings.update({key: value for key, value in data.items() if isinstance(value, str)})
        return settings

    def save(self, settings: dict) -> None:
        current = self.load()
        current.update(settings)
        self.config_path.write_text(
            json.dumps(current, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
