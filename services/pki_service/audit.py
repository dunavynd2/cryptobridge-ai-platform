import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_lock = threading.Lock()
_logger = logging.getLogger("pki_audit")

AUDIT_LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "pki_audit.log"


def record_event(actor: str, action: str, target: str, result: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """Append an immutable-style audit entry (timestamp, actor, action, target, result, reason)."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "target": target,
        "result": result,
        "reason": reason,
    }
    with _lock:
        try:
            AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(AUDIT_LOG_PATH, "a") as log_file:
                log_file.write(json.dumps(event) + "\n")
        except OSError:
            _logger.warning("Failed to write PKI audit log entry", exc_info=True)
    return event
