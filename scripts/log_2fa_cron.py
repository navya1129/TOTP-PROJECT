#!/usr/bin/env python3
import os
import datetime
import pyotp
import base64

DATA_PATH = "/data/seed.txt"

def main():
    if not os.path.exists(DATA_PATH):
        print("Seed not found")
        return

    with open(DATA_PATH, "r") as f:
        seed_hex = f.read().strip()

    # Convert hex → Base32 for pyotp
    seed_bytes = bytes.fromhex(seed_hex)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
