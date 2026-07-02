# CryptoBridge AI Platform

An AI-powered autonomous cybersecurity engineering platform...

## Instructions
See `INSTRUCTIONS.md` and individual `*_INSTRUCTIONS.md` files in agents/ and elsewhere for detailed usage and extension guides.

Full details in docs/ and original vision.

## PKI Management Microservice
A working implementation of `specs/pki-management-microservice.md` lives in `services/pki_service/`. It issues, retrieves, and revokes X.509 certificates signed by an in-memory root CA.

```bash
pip install -r requirements.txt
uvicorn services.pki_service.main:app --reload
```

- `GET /ca/root` — root CA certificate (public)
- `POST /certificates/issue` — issue a certificate (requires `X-API-Key`, role `admin` or `service`)
- `GET /certificates/{cert_id}` — certificate metadata/status (requires `X-API-Key`)
- `POST /certificates/revoke` — revoke a certificate (requires `X-API-Key`, role `admin`)

Dev API keys default to `dev-admin-key` (admin) and `dev-service-key` (service); override via the `PKI_API_KEYS` env var (`key:role,key:role`) in production. Storage is in-memory (swap `services/pki_service/store.py` for a PostgreSQL-backed implementation per the spec's Architecture section). Tests: `pytest tests/`.