import os
from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import Header, HTTPException, status


@dataclass
class Principal:
    api_key: str
    role: str


def _load_api_keys() -> Dict[str, str]:
    """Load `api_key:role` pairs from PKI_API_KEYS, e.g. "key1:admin,key2:service".

    Falls back to development defaults so the service is usable out of the
    box; override PKI_API_KEYS in production.
    """
    raw = os.environ.get("PKI_API_KEYS", "dev-admin-key:admin,dev-service-key:service")
    keys: Dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        key, _, role = pair.partition(":")
        keys[key] = role or "service"
    return keys


def require_role(*allowed_roles: str):
    def dependency(x_api_key: Optional[str] = Header(default=None)) -> Principal:
        api_keys = _load_api_keys()
        if not x_api_key or x_api_key not in api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )
        role = api_keys[x_api_key]
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation",
            )
        return Principal(api_key=x_api_key, role=role)

    return dependency
