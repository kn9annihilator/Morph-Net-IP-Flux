# core/tls_manager.py

import os
import logging
import datetime
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def rotate_tls_cert(label="rotated_tls", cn="myserver.local", cert_dir="certs", validity_days=365):
    """
    Generate a self-signed TLS certificate and private key.

    Args:
        label (str): Base name for certificate and key files.
        cn (str): Common Name for the certificate.
        cert_dir (str): Directory to save cert and key.
        validity_days (int): Validity period of certificate.

    Returns:
        tuple: (cert_file_path, key_file_path)
    """
    try:
        os.makedirs(cert_dir, exist_ok=True)

        cert_path = os.path.join(cert_dir, f"{label}_cert.pem")
        key_path = os.path.join(cert_dir, f"{label}_key.pem")

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, cn)
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=validity_days))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(cn)]),
                critical=False,
            )
            .sign(key, hashes.SHA256(), default_backend())
        )

        # Save the key
        with open(key_path, "wb") as kf:
            kf.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Save the cert
        with open(cert_path, "wb") as cf:
            cf.write(cert.public_bytes(serialization.Encoding.PEM))

        expiry = cert.not_valid_after.replace(tzinfo=datetime.timezone.utc)
        logging.info(f"Generated TLS cert: {cert_path} (expires: {expiry})")

        return cert_path, key_path

    except Exception as e:
        logging.error(f"TLS certificate generation failed: {e}")
        return None, None


if __name__ == "__main__":
    logging.basicConfig(
        filename="logs/rotation.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    cert_path, key_path = rotate_tls_cert()
    print(f"Cert: {cert_path}\nKey: {key_path}")
