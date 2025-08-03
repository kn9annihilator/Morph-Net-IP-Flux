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
    """
    Generates a new, self-signed TLS certificate with randomized attributes.

    This function is a core component of the MTD strategy, designed to defeat
    TLS fingerprinting techniques like JA3/JA3S by ensuring that the server's
    cryptographic identity changes with each rotation cycle.

    Args:
        config (dict): The global configuration dictionary which contains the
                       'tls' section with all necessary parameters.

    Returns:
        tuple: A tuple containing the file paths to the new certificate and
               private key (cert_path, key_path), or (None, None) on failure.
    """
    try:
        # --- 1. Load Configuration ---
        # Extract the TLS-specific configuration dictionary.
        # Provide default values to prevent crashes if the config is incomplete.
        tls_config = config.get("tls", {})
        cert_dir = tls_config.get("cert_dir", "certs")
        validity_days = tls_config.get("validity_days", 90)

        # --- 2. Randomize Certificate Identity ---
        # To make fingerprinting difficult, we randomly select key details
        # for the certificate's subject from lists defined in the config file.
        cn_list = tls_config.get("common_names", ["default.server.local"])
        org_list = tls_config.get("organization_names", ["Default Organization Inc."])
        
        random_common_name = random.choice(cn_list)
        random_organization = random.choice(org_list)

        logging.info(f"Generating new TLS certificate with CN='{random_common_name}' and O='{random_organization}'...")

        # --- 3. Prepare File Paths and Directories ---
        os.makedirs(cert_dir, exist_ok=True)
        # We use fixed filenames because the web server (e.g., Nginx) will be
        # configured to point to these specific files. The randomness is inside
        # the certificate content, not the filename.
        cert_path = os.path.join(cert_dir, "rotated_cert.pem")
        key_path = os.path.join(cert_dir, "rotated_key.pem")

        # --- 4. Generate a New Private Key ---
        # A new private key is generated for each certificate to ensure that
        # even if an old key is compromised, it cannot be used to decrypt
        # new sessions.
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # --- 5. Build the Certificate's Subject and Issuer Information ---
        # For a self-signed certificate, the subject (who the certificate is for)
        # and the issuer (who signed it) are the same.
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, random_organization),
            x509.NameAttribute(NameOID.COMMON_NAME, random_common_name),
        ])

        # --- 6. Construct the Certificate Object ---
        # We use a certificate builder to assemble all the parts.
        cert_builder = x509.CertificateBuilder()
        certificate = (
            cert_builder.subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            # Use a random serial number for each certificate. This is another
            # critical element for defeating fingerprinting.
            .serial_number(x509.random_serial_number())
            # Set the validity period. The start time is now.
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            # The end time is now + the configured number of days.
            .not_valid_after(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=validity_days)
            )
            # Add the Subject Alternative Name (SAN), which is required by
            # modern browsers.
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(random_common_name)]),
                critical=False,
            )
            # Sign the certificate with our own private key.
            .sign(private_key, hashes.SHA256())
        )

        # --- 7. Save the Private Key to a File ---
        # The key is saved in PEM format, which is a standard text-based format.
        # It is saved without encryption for easy use by the web server.
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # --- 8. Save the Certificate to a File ---
        # The certificate is also saved in PEM format.
        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

        # --- 9. Log Success and Return Paths ---
        # Use the non-deprecated attribute for timezone-aware expiry date.
        expiry_date = certificate.not_valid_after_utc
        logging.info(f"[OK] Generated new TLS cert. Expires: {expiry_date.strftime('%Y-%m-%d')}")
        return cert_path, key_path

    except Exception as e:
        # Log any errors that occur during the process.
        logging.error(f"TLS certificate generation failed: {e}", exc_info=True)
        return None, None