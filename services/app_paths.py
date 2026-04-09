import os
from pathlib import Path


def get_app_data_dir(app_name: str = "walkdist") -> Path:
    candidate_dirs = [
        Path(os.getenv("LOCALAPPDATA") or ""),
        Path(os.getenv("APPDATA") or ""),
        Path.home(),
        Path.cwd() / ".walkdist-data",
    ]

    for base_dir in candidate_dirs:
        if not str(base_dir):
            continue

        app_dir = base_dir / app_name if base_dir.name != ".walkdist-data" else base_dir
        try:
            app_dir.mkdir(parents=True, exist_ok=True)
            return app_dir
        except OSError:
            continue

    raise OSError("walkdist 설정 폴더를 생성할 수 없습니다.")
