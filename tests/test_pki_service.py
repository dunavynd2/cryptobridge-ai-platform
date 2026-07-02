from fastapi.testclient import TestClient

from services.pki_service.main import app

ADMIN_KEY = "dev-admin-key"
SERVICE_KEY = "dev-service-key"

client = TestClient(app)


def _issue(common_name="example.internal", **overrides):
    payload = {
        "common_name": common_name,
        "san": [common_name],
        "validity_days": 30,
        "key_type": "ECC",
    }
    payload.update(overrides)
    return client.post("/certificates/issue", json=payload, headers={"X-API-Key": SERVICE_KEY})


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_get_root_ca():
    resp = client.get("/ca/root")
    assert resp.status_code == 200
    assert "BEGIN CERTIFICATE" in resp.json()["certificate_pem"]


def test_issue_requires_api_key():
    resp = client.post("/certificates/issue", json={"common_name": "no-auth.internal"})
    assert resp.status_code == 401


def test_issue_rejects_unknown_api_key():
    resp = client.post(
        "/certificates/issue",
        json={"common_name": "bad-key.internal"},
        headers={"X-API-Key": "not-a-real-key"},
    )
    assert resp.status_code == 401


def test_issue_and_get_certificate():
    issue_resp = _issue("service-a.internal")
    assert issue_resp.status_code == 201
    body = issue_resp.json()
    assert "BEGIN CERTIFICATE" in body["certificate_pem"]
    assert "BEGIN PRIVATE KEY" in body["private_key_pem"]
    cert_id = body["cert_id"]

    get_resp = client.get(f"/certificates/{cert_id}", headers={"X-API-Key": SERVICE_KEY})
    assert get_resp.status_code == 200
    meta = get_resp.json()
    assert meta["status"] == "active"
    assert meta["common_name"] == "service-a.internal"


def test_issue_rsa_certificate():
    resp = _issue("rsa-service.internal", key_type="RSA")
    assert resp.status_code == 201
    assert "BEGIN CERTIFICATE" in resp.json()["certificate_pem"]


def test_get_unknown_certificate_returns_404():
    resp = client.get("/certificates/does-not-exist", headers={"X-API-Key": SERVICE_KEY})
    assert resp.status_code == 404


def test_revoke_certificate_requires_admin_role():
    issue_resp = _issue("revoke-me.internal")
    cert_id = issue_resp.json()["cert_id"]

    forbidden = client.post(
        "/certificates/revoke",
        json={"cert_id": cert_id, "reason": "test"},
        headers={"X-API-Key": SERVICE_KEY},
    )
    assert forbidden.status_code == 403

    revoked = client.post(
        "/certificates/revoke",
        json={"cert_id": cert_id, "reason": "key-compromise"},
        headers={"X-API-Key": ADMIN_KEY},
    )
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"
    assert revoked.json()["revocation_reason"] == "key-compromise"


def test_revocation_propagates_to_get():
    issue_resp = _issue("propagation.internal")
    cert_id = issue_resp.json()["cert_id"]
    client.post(
        "/certificates/revoke",
        json={"cert_id": cert_id, "reason": "superseded"},
        headers={"X-API-Key": ADMIN_KEY},
    )
    get_resp = client.get(f"/certificates/{cert_id}", headers={"X-API-Key": SERVICE_KEY})
    assert get_resp.json()["status"] == "revoked"


def test_revoke_already_revoked_certificate_conflicts():
    issue_resp = _issue("double-revoke.internal")
    cert_id = issue_resp.json()["cert_id"]
    client.post(
        "/certificates/revoke",
        json={"cert_id": cert_id, "reason": "r1"},
        headers={"X-API-Key": ADMIN_KEY},
    )
    second = client.post(
        "/certificates/revoke",
        json={"cert_id": cert_id, "reason": "r2"},
        headers={"X-API-Key": ADMIN_KEY},
    )
    assert second.status_code == 409


def test_revoke_unknown_certificate_returns_404():
    resp = client.post(
        "/certificates/revoke",
        json={"cert_id": "missing", "reason": "n/a"},
        headers={"X-API-Key": ADMIN_KEY},
    )
    assert resp.status_code == 404


def test_validity_days_beyond_baseline_maximum_rejected():
    resp = _issue("too-long.internal", validity_days=10000)
    assert resp.status_code == 422


def test_common_name_required():
    resp = client.post(
        "/certificates/issue",
        json={"common_name": ""},
        headers={"X-API-Key": SERVICE_KEY},
    )
    assert resp.status_code == 422
