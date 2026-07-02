from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status

from .audit import record_event
from .auth import Principal, require_role
from .ca import get_root_ca
from .certs import issue_certificate
from .models import CertMetadata, CertRequest, CertResponse, RevokeRequest
from .ratelimit import rate_limit_middleware
from .store import get_store

app = FastAPI(
    title="CryptoBridge PKI Management Microservice",
    version="1.0.0",
    description=(
        "Secure, automated PKI service for issuing, retrieving, and revoking "
        "X.509 certificates in the CryptoBridge platform."
    ),
)

app.middleware("http")(rate_limit_middleware)


def _to_metadata(record: dict) -> CertMetadata:
    return CertMetadata(
        cert_id=record["cert_id"],
        common_name=record["common_name"],
        san=record["san"],
        certificate_pem=record["certificate_pem"],
        expiry=record["expiry"],
        status=record["status"],
        issued_at=record["issued_at"],
        revoked_at=record.get("revoked_at"),
        revocation_reason=record.get("revocation_reason"),
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ca/root")
def get_root_ca_cert() -> dict:
    root_ca = get_root_ca()
    return {"certificate_pem": root_ca.certificate_pem}


@app.post("/certificates/issue", response_model=CertResponse, status_code=status.HTTP_201_CREATED)
def issue(
    request: CertRequest, principal: Principal = Depends(require_role("admin", "service"))
) -> CertResponse:
    record = issue_certificate(request)
    record["status"] = "active"
    get_store().save(record)
    record_event(actor=principal.api_key, action="issue", target=record["cert_id"], result="success")
    return CertResponse(
        cert_id=record["cert_id"],
        certificate_pem=record["certificate_pem"],
        private_key_pem=record["private_key_pem"],
        expiry=record["expiry"],
        status=record["status"],
    )


@app.get("/certificates/{cert_id}", response_model=CertMetadata)
def get_certificate(
    cert_id: str, principal: Principal = Depends(require_role("admin", "service"))
) -> CertMetadata:
    record = get_store().get(cert_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    if record["status"] == "active" and record["expiry"] < datetime.now(timezone.utc):
        record["status"] = "expired"
    return _to_metadata(record)


@app.post("/certificates/revoke", response_model=CertMetadata)
def revoke_certificate(
    request: RevokeRequest, principal: Principal = Depends(require_role("admin"))
) -> CertMetadata:
    existing = get_store().get(request.cert_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    if existing["status"] == "revoked":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Certificate already revoked")

    record = get_store().revoke(request.cert_id, request.reason, datetime.now(timezone.utc))
    record_event(
        actor=principal.api_key,
        action="revoke",
        target=request.cert_id,
        result="success",
        reason=request.reason,
    )
    return _to_metadata(record)
