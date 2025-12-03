import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

# -----------------------------
# Step 5: Decrypt seed
# -----------------------------
def decrypt_seed(encrypted_seed_b64: str, private_key_pem_path: str) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256  
    Returns: 64-character hex seed string
    """

    # Load private key
    with open(private_key_pem_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # Decode base64 → bytes
    ciphertext = base64.b64decode(encrypted_seed_b64)

    # Decrypt using RSA-OAEP with SHA-256
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decode bytes → UTF-8 string
    hex_seed = plaintext.decode("utf-8")

    # Must be a 64-character hex string
    assert len(hex_seed) == 64

    return hex_seed


# -----------------------------
# Step 6: Generate TOTP
# -----------------------------
def generate_totp_code(hex_seed: str) -> str:
    """
    Generate a 6-digit TOTP code from a 64-character hex seed
    """

    # Convert hex seed → bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # Convert bytes → Base32 (TOTP requires Base32)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    # Generate TOTP (30-second window, 6 digits)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)

    return totp.now()


# -----------------------------
# Step 6: Verify TOTP
# -----------------------------
def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code with ±1 time window tolerance
    """

    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)

    return totp.verify(code, valid_window=valid_window)
