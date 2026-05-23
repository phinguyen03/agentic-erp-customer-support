import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

_STORE_PATH = Path(__file__).parent.parent / "data" / "pending_approvals.json"


def _load() -> dict:
    if not _STORE_PATH.exists():
        return {}
    text = _STORE_PATH.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else {}


def _save(store: dict) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")


def submit_approval(user_id: str, order_id: str, action: str, amount: float) -> str:
    store = _load()
    existing = next(
        (v for v in store.values() if v["user_id"] == user_id and v["order_id"] == order_id and v["status"] == "pending"),
        None,
    )
    if existing:
        logging.info("reusing approval %s for user %s order %s", existing["request_id"], user_id, order_id)
        return existing["request_id"]
    request_id = str(uuid4())[:8]
    store[request_id] = {
        "request_id": request_id,
        "user_id": user_id,
        "order_id": order_id,
        "action": action,
        "amount": amount,
        "status": "pending",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "decided_at": None,
        "decided_by": None,
    }
    _save(store)
    logging.info("submitted approval %s for user %s order %s", request_id, user_id, order_id)
    return request_id


def get_user_approvals(user_id: str) -> list[dict]:
    store = _load()
    return [v for v in store.values() if v["user_id"] == user_id]


def decide(request_id: str, status: str, decided_by: str = "manager") -> bool:
    store = _load()
    if request_id not in store:
        return False
    store[request_id]["status"] = status
    store[request_id]["decided_at"] = datetime.now(timezone.utc).isoformat()
    store[request_id]["decided_by"] = decided_by
    _save(store)
    logging.info("approval %s -> %s by %s", request_id, status, decided_by)
    return True
