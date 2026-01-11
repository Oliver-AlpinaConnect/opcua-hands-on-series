import datetime
import ipaddress
import os
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_self_signed_cert():
    # 1. Get the local hostname dynamically
    hostname = socket.gethostname()
    
    # 2. Setup the output directory
    output_dir = "certs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    app_uri = "urn:fan:control:opc-ua:server"

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Asyncua Project"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname), # Also updated Common Name
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.UTC))
        .not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365))
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName(hostname), # <--- Dynamically sets the device name
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                x509.UniformResourceIdentifier(app_uri),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # 3. Save files into the 'certs/' folder
    key_path = os.path.join(output_dir, "server_key.pem")
    cert_path = os.path.join(output_dir, "server_cert.der")

    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))

    print(f"Certificates generated for: {hostname}")
    print(f"Files saved in: {output_dir}/")

if __name__ == "__main__":
    generate_self_signed_cert()