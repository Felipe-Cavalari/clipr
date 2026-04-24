"""
Persistência de preferências do usuário em ~/.clipr/config.json
"""

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".clipr"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get(key: str) -> Any:
    return _load().get(key)


def set(key: str, value: Any) -> None:
    data = _load()
    data[key] = value
    _save(data)
