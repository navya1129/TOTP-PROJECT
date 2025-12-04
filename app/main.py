from fastapi import FastAPI, HTTPException
import os
import time

from crypto_utils import decrypt_seed, generate_totp_code, verify_totp_code

app = FastAPI()

# Paths inside container
DATA_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "/app/student_private.pem"

# ------------------------
# POST /decrypt-seed
# ------------------------
@app.post("/decrypt-seed")
def decrypt_seed_api(body: dict):
    if "encrypted_seed" not in body:
        raise HTTPException(400, "Missing encrypted_seed")

    try:
        seed_hex = decrypt_seed(body["encrypted_seed"], PRIVATE_KEY_PATH)
    except Exception as e:
        raise HTTPException(500, str(e))

    # Save decrypted seed to persistent volume
    os.makedirs("/data", exist_ok=True)
    with open(DATA_PATH, "w") as f:
        f.write(seed_hex)

    return {"status": "ok"}


# ------------------------
# GET /generate-2fa
# ------------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(DATA_PATH):
        raise HTTPException(500, "Seed not decrypted yet")

    with open(DATA_PATH, "r") as f:
        seed_hex = f.read().strip()

    code = generate_totp_code(seed_hex)
    remaining = 30 - (int(time.time()) % 30)

    return {
        "code": code,
        "valid_for": remaining
    }


# ------------------------
# POST /verify-2fa
# ------------------------
@app.post("/verify-2fa")
def verify_2fa(body: dict):
    if "code" not in body:
        raise HTTPException(400, "Missing code")

    if not os.path.exists(DATA_PATH):
        raise HTTPException(500, "Seed not decrypted yet")

    with open(DATA_PATH, "r") as f:
        seed_hex = f.read().strip()

    valid = verify_totp_code(seed_hex, body["code"])

    return {"valid": valid}
