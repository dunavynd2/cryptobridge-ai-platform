import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from .ca import get_root_ca
from .models import CertRequest


def _generate_key_pair(key_type: str):
    if key_type == "RSA":
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return ec.generate_private_key(ec.SECP384R1())


def issue_certificate(request: CertRequest) -> Dict[str, Any]:
    """Issue a new leaf certificate signed by the service's root CA.

    The private key is generated server-side and returned exactly once in
    the response; it is never persisted or logged.
    """
    root_ca = get_root_ca()
    private_key = _generate_key_pair(request.key_type)

    effective_san = request.san if request.san else [request.common_name]
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, request.common_name)])
    now = datetime.now(timezone.utc)
    not_after = now + timedelta(days=request.validity_days)

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(root_ca.certificate.subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=request.key_type == "RSA",
                key_agreement=request.key_type == "ECC",
                content_commitment=False,
                data_encipherment=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(name) for name in effective_san]),
            critical=False,
        )
    )

    certificate = builder.sign(root_ca.private_key, hashes.SHA384())

    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM).decode()
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    return {
        "cert_id": str(uuid.uuid4()),
        "certificate_pem": certificate_pem,
        "private_key_pem": private_key_pem,
        "expiry": not_after,
        "common_name": request.common_name,
        "san": effective_san,
        "issued_at": now,
    }
