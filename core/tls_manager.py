# core/tls_manager.py

import os
import logging
import datetime
import random
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

def rotate_tls_cert(config: dict):
    """Generates a self-signed TLS certificate with randomized attributes from the config."""
    try:
        tls_config = config.get("tls", {})
        cert_dir = tls_config.get("cert_dir", "certs")
        validity_days = tls_config.get("validity_days", 90)
        
        # Randomize certificate attributes for better fingerprint evasion
        cn = random.choice(tls_config.get("common_names", ["fallback.local"]))
        org = random.choice(tls_config.get("organization_names", ["Fallback Inc."]))

        os.makedirs(cert_dir, exist_ok=True)
        # Use fixed filenames. The randomness is inside the certificate itself.
        cert_path = os.path.join(cert_dir, "rotated_cert.pem")
        key_path = os.path.join(cert_dir, "rotated_key.pem")

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
            x509.NameAttribute(NameOID.COMMON_NAME, cn),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=validity_days))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
            .sign(key, hashes.SHA256())
        )

        with open(key_path, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        expiry = cert.not_valid_after_utc
        logging.info(f"[OK] Generated new TLS cert (CN={cn}). Expires: {expiry.strftime('%Y-%m-%d')}")
        return cert_path, key_path

    except Exception as e:
        logging.error(f"TLS certificate generation failed: {e}", exc_info=True)
        return None, None