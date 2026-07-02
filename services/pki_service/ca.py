from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID


class RootCA:
    """Self-signed root CA used to sign all certificates issued by this service.

    Generated in-memory per process. A production deployment would load the
    root key from a secrets manager (Azure Key Vault / HashiCorp Vault) instead.
    """

    def __init__(self, common_name: str = "CryptoBridge Root CA", validity_years: int = 10):
        self.private_key = ec.generate_private_key(ec.SECP384R1())
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CryptoBridge AI Platform"),
            ]
        )
        now = datetime.now(timezone.utc)
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=365 * validity_years))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(self.private_key.public_key()),
                critical=False,
            )
        )
        self.certificate = builder.sign(self.private_key, hashes.SHA384())

    @property
    def certificate_pem(self) -> str:
        return self.certificate.public_bytes(serialization.Encoding.PEM).decode()


_root_ca: Optional[RootCA] = None


def get_root_ca() -> RootCA:
    """Return the process-wide root CA, generating it on first use."""
    global _root_ca
    if _root_ca is None:
        _root_ca = RootCA()
    return _root_ca
