import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def load_private_key(path="student_private.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_seed(encrypted_seed_b64):
    try:
        encrypted = base64.b64decode(encrypted_seed_b64)

        private_key = load_private_key()

        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        seed_hex = decrypted.decode()

        if len(seed_hex) != 64:
            raise ValueError("Invalid seed length")

        return seed_hex
    except Exception:
        return None
