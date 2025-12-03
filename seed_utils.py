import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

def decrypt_seed(encrypted_seed_b64: str, private_key_pem_path: str) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256  
    Returns: 64-character hex seed string
    """
    # load private key
    with open(private_key_pem_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    # decode base64 to bytes
    ciphertext = base64.b64decode(encrypted_seed_b64)
    # decrypt
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # decode to utf-8 string
    hex_seed = plaintext.decode('utf-8')
    # validate: must be 64-char hex
    assert len(hex_seed) == 64
    # you can add more checks if needed
    return hex_seed

def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP 6-digit code from 64-char hex seed
    """
    # convert hex seed to bytes
    seed_bytes = bytes.fromhex(hex_seed)
    # base32 encode -> required format for TOTP libs
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    # create TOTP object (30s period, 6 digits, SHA-1 by default)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()

def verify_totp_code(hex_seed: str, code: str, window: int = 1) -> bool:
    """
    Verify a TOTP code with ± window (default ±1 period) tolerance
    """
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=window)
