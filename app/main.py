from fastapi import FastAPI, HTTPException
import pyotp
import time
import os

from crypto_utils import decrypt_seed

app = FastAPI()

DATA_PATH = "/data/seed.txt"

# ------------------------
# POST /decrypt-seed
# ------------------------
@app.post("/decrypt-seed")
def decrypt_seed_api(body: dict):
    if "encrypted_seed" not in body:
        raise HTTPException(400, "Missing encrypted_seed")

    seed_hex = decrypt_seed(body["encrypted_seed"])

    if seed_hex is None:
        raise HTTPException(500, "Decryption failed")

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

    secret = pyotp.TOTP(seed_hex)
    code = secret.now()
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

    totp = pyotp.TOTP(seed_hex)

    valid = (
        totp.verify(body["code"], valid_window=1)
    )

    return {"valid": valid}
