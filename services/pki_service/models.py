from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CertRequest(BaseModel):
    common_name: str = Field(..., min_length=1, max_length=255)
    san: List[str] = Field(default_factory=list)
    # 825 days matches the CA/Browser Forum baseline maximum validity for TLS certs.
    validity_days: int = Field(default=365, ge=1, le=825)
    key_type: Literal["ECC", "RSA"] = "ECC"


class CertResponse(BaseModel):
    cert_id: str
    certificate_pem: str
    private_key_pem: str
    expiry: datetime
    status: str


class CertMetadata(BaseModel):
    cert_id: str
    common_name: str
    san: List[str]
    certificate_pem: str
    expiry: datetime
    status: str
    issued_at: datetime
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None


class RevokeRequest(BaseModel):
    cert_id: str
    reason: str = "unspecified"
