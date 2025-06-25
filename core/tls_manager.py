 # core/tls_manager.py

import os
import logging
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# ---------------------------
# TLS Configuration
# ---------------------------
CERTS_DIR = "certs"
KEY_SIZE = 2048
CERT_VALIDITY_DAYS = 2
DEFAULT_CN = "MorphNetIPFlux.local"

# ---------------------------
# Logger Setup
# ---------------------------
def setup_logger():
    logging.basicConfig(
        filename="logs/rotation.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

# ---------------------------
# Generate RSA Key Pair
# ---------------------------
def generate_key_pair():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=KEY_SIZE,
    )

# ---------------------------
# Generate Self-Signed Certificate
# ---------------------------
def generate_self_signed_cert(private_key, common_name):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"IN"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MorphNetIPFlux"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=CERT_VALIDITY_DAYS))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(common_name)]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )
    return cert

# ---------------------------
# Write Key and Cert to Files
# ---------------------------
def write_tls_files(cert, key, label):
    if not os.path.exists(CERTS_DIR):
        os.makedirs(CERTS_DIR)

    cert_file = os.path.join(CERTS_DIR, f"{label}_cert.pem")
    key_file = os.path.join(CERTS_DIR, f"{label}_key.pem")

    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_file, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    logging.info(f"Generated new TLS cert: {cert_file}, expires on {cert.not_valid_after}")
    return cert_file, key_file

# ---------------------------
# Public Function for Rotation
# ---------------------------
def rotate_tls_cert(label="ephemeral_tls", cn=DEFAULT_CN):
    setup_logger()
    try:
        private_key = generate_key_pair()
        cert = generate_self_signed_cert(private_key, cn)
        cert_path, key_path = write_tls_files(cert, private_key, label)
        return cert_path, key_path
    except Exception as e:
        logging.error(f"TLS rotation failed: {e}")
        return None, None

# ---------------------------
# Manual Trigger for Testing
# ---------------------------
if __name__ == "__main__":
    cert_path, key_path = rotate_tls_cert()
    print("Cert:", cert_path)
    print("Key:", key_path)

