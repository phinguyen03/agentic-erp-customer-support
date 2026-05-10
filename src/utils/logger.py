import logging
import sys
from contextvars import ContextVar

_thread_id_var: ContextVar[str] = ContextVar("thread_id", default="-")
_user_id_var: ContextVar[str] = ContextVar("user_id", default="-")

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | [thread=%(thread_id)s user=%(user_id)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class _ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.thread_id = _thread_id_var.get()
        record.user_id = _user_id_var.get()
        return True


def _configure_root() -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT))
    handler.addFilter(_ContextFilter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)


_configure_root()


def set_log_context(thread_id: str, user_id: str) -> None:
    _thread_id_var.set(thread_id)
    _user_id_var.set(user_id)
