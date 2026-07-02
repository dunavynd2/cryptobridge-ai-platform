# Spec Sheet: PKI Management Microservice

**Project**: CryptoBridge AI Platform  
**Component**: PKI Management Microservice  
**Version**: 1.0  
**Date**: July 2026  
**Status**: Core issuance/retrieval/revocation implemented (in-memory storage) — see `services/pki_service/`. Automatic renewal, PostgreSQL persistence, and Key Vault integration are not yet implemented.  
**Owner**: Orchestrator / Autonomous Agents

## 1. Overview
**Purpose**: Provide a secure, automated Public Key Infrastructure (PKI) service for managing certificates in a crypto bridge environment (e.g., TLS for inter-service communication, client auth, revocation).

**Scope**:
- Certificate issuance, renewal, revocation.
- Integration with external CAs or internal root CA.
- Secure storage and auditing.
- Compliance with industry standards.

**Out of Scope**: Full HSM integration (Phase 2), advanced OCSP stapling.

**Key Benefits**: Reduces manual cert management, enforces crypto best practices, supports autonomous operations.

## 2. Functional Requirements
1. **Certificate Lifecycle Management**
   - Issue X.509 certificates (RSA/ECC).
   - Automatic renewal (e.g., 30 days before expiry).
   - Revocation (CRL/OCSP support).

2. **API Endpoints** (FastAPI)
   - `POST /certificates/issue` — Issue new cert.
   - `GET /certificates/{id}` — Retrieve details/status.
   - `POST /certificates/revoke` — Revoke cert.
   - `GET /ca/root` — Serve root CA cert.

3. **Authentication & Authorization**
   - mTLS or API keys for internal services.
   - Role-based access (admin vs. service).

4. **Auditing & Logging**
   - All operations logged with timestamps, actor, reason.
   - Immutable audit trail.

## 3. Non-Functional Requirements
- **Security** (Cryptography Agent input):
  - TLS 1.3 only.
  - ECC P-384 or post-quantum ready (e.g., Kyber hybrid).
  - Secrets management (Azure Key Vault or HashiCorp Vault).
  - Input validation, rate limiting, OWASP Top 10 compliance.
- **Performance**: < 500ms for cert issuance under load.
- **Scalability**: Stateless where possible; use Redis for sessions.
- **Reliability**: 99.9% uptime; retries on DB failures.
- **Compliance**: NIST SP 800-57, RFC 5280, FIPS 140-2/3 where applicable.

## 4. Architecture
- **Backend**: FastAPI + Python 3.11.
- **Database**: PostgreSQL (certs, revocations, audits).
- **Cache**: Redis.
- **Storage**: Encrypted volumes for private keys.
- **Deployment**: Docker + Azure Container Apps (future).

## 5. Data Models (Pydantic)
```python
class CertRequest(BaseModel):
    common_name: str
    san: List[str]
    validity_days: int = 365
    key_type: Literal["ECC", "RSA"] = "ECC"

class CertResponse(BaseModel):
    cert_id: str
    certificate_pem: str
    private_key_pem: str  # Only for initial issuance, secured
    expiry: datetime
    status: str
```

## 6. Dependencies & Integrations
- `cryptography` library.
- `asyncpg` for Postgres.
- Azure SDK (identity, keyvault).
- Testing: pytest + httpx.

## 7. Security Considerations (from Research/Crypto Agents)
- Certificate validation per RFC 5280 / NIST.
- Protect private keys (never log, use memory-only where possible).
- Rate limiting and WAF.
- Threat modeling: MITRE ATT&CK for credential access.

## 8. Testing Requirements (Testing Agent)
- Unit: 90%+ coverage.
- Integration: End-to-end cert flow.
- Security: bandit, semgrep, manual pen-test recommendations.
- Edge cases: Expired certs, invalid CSRs, high load, revocation propagation.

## 9. Success Criteria
- Coding Agent produces working code.
- All tests pass.
- Documentation generated.
- Deployable Docker image.

## 10. References
- NIST SP 800-52 Rev. 2 (TLS Guidelines).
- RFC 5280 (Internet X.509 PKI).
- OWASP Cryptographic Storage Cheat Sheet.