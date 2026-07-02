import threading
from datetime import datetime
from typing import Any, Dict, List, Optional


class CertificateStore:
    """Thread-safe in-memory certificate store.

    Swap this for a PostgreSQL-backed implementation (see spec 'Architecture')
    once persistence is required; the FastAPI layer only depends on this
    save/get/revoke interface.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._certs: Dict[str, Dict[str, Any]] = {}

    def save(self, record: Dict[str, Any]) -> None:
        with self._lock:
            self._certs[record["cert_id"]] = dict(record)

    def get(self, cert_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._certs.get(cert_id)
            return dict(record) if record is not None else None

    def revoke(self, cert_id: str, reason: str, revoked_at: datetime) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._certs.get(cert_id)
            if record is None:
                return None
            record["status"] = "revoked"
            record["revoked_at"] = revoked_at
            record["revocation_reason"] = reason
            return dict(record)

    def all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(record) for record in self._certs.values()]


_store: Optional[CertificateStore] = None


def get_store() -> CertificateStore:
    global _store
    if _store is None:
        _store = CertificateStore()
    return _store
