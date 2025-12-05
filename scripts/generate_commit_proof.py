import base64
import subprocess
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

# --------------------------
# 1️⃣ Get current commit hash
# --------------------------
def get_commit_hash() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True,
        text=True,
        check=True
    )
    commit_hash = result.stdout.strip()
    if len(commit_hash) != 40:
        raise ValueError("Commit hash must be 40 characters")
    return commit_hash

# --------------------------
# 2️⃣ Sign commit hash
# --------------------------
def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message (ASCII commit hash) using RSA-PSS-SHA256
    """
    message_bytes = message.encode('utf-8')
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# --------------------------
# 3️⃣ Encrypt signature
# --------------------------
def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP-SHA256
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# --------------------------
# 4️⃣ Load keys
# --------------------------
def load_private_key(path: str):
    with open(path, "rb") as f:
        return load_pem_private_key(f.read(), password=None)

def load_public_key(path: str):
    with open(path, "rb") as f:
        return load_pem_public_key(f.read())

# --------------------------
# 5️⃣ Generate commit proof
# --------------------------
def generate_commit_proof():
    # Get commit hash
    commit_hash = get_commit_hash()
    print("Commit Hash:", commit_hash)

    # Load student private key
    student_private_key = load_private_key("student_private.pem")

    # Sign commit hash
    signature = sign_message(commit_hash, student_private_key)

    # Load instructor public key
    instructor_public_key = load_public_key("instructor_public.pem")

    # Encrypt signature
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)

    # Base64 encode
    b64_signature = base64.b64encode(encrypted_signature).decode('utf-8')
    print("Encrypted Signature (Base64):", b64_signature)

    return commit_hash, b64_signature

# --------------------------
# 6️⃣ Run
# --------------------------
if __name__ == "__main__":
    generate_commit_proof()
