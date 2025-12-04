import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp
import time

# -------------------------
# Load Private Key
# -------------------------
def load_private_key(path="/app/student_private.pem"):
    """Load RSA private key from PEM file."""
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


# -------------------------
# Decrypt Seed
# -------------------------
def decrypt_seed(encrypted_seed_b64, private_key_path="/app/student_private.pem"):
    """Decrypt a base64-encoded seed using RSA-OAEP with SHA-256."""
    try:
        encrypted = base64.b64decode(encrypted_seed_b64)
        private_key = load_private_key(private_key_path)

        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        seed_hex = decrypted.decode().strip()

        # Validate 64-character hex
        if len(seed_hex) != 64:
            raise ValueError("Invalid seed length")
        if not all(c in "0123456789abcdefABCDEF" for c in seed_hex):
            raise ValueError("Seed contains non-hex characters")

        return seed_hex

    except Exception as e:
        raise Exception(f"Decryption failed: {e}")


# -------------------------
# Generate TOTP
# -------------------------
def generate_totp_code(hex_seed):
    """Generate a 6-digit TOTP code from 64-character hex seed."""
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()


# -------------------------
# Verify TOTP
# -------------------------
def verify_totp_code(hex_seed, code, valid_window=1):
    """Verify TOTP code with ±1 period tolerance."""
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)
