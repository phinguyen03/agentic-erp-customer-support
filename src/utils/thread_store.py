import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import src.utils.logger  # noqa: F401 — configure root logger on import

_STORE_PATH = Path(__file__).parent.parent / "data" / "threads.json"


def _load() -> dict:
    if not _STORE_PATH.exists():
        return {}
    return json.loads(_STORE_PATH.read_text(encoding="utf-8"))


def _save(store: dict) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")


def save_thread(user_id: str, thread_id: str) -> None:
    store = _load()
    store[user_id] = {
        "thread_id": thread_id,
        "last_active": datetime.now(timezone.utc).isoformat(),
    }
    _save(store)
    logging.info("saved thread %s for user %s", thread_id, user_id)


def load_thread(user_id: str) -> str | None:
    store = _load()
    entry = store.get(user_id)
    if entry:
        logging.info("resumed thread %s for user %s", entry["thread_id"], user_id)
        return entry["thread_id"]
    return None
