import requests
import json
import sys
import os

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def find_public_key(possible_paths):
    """Find student_public.pem in multiple folders"""
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def request_seed(student_id, github_repo_url, api_url=API_URL):
    # 1️⃣ Find public key
    possible_paths = ["app/student_public.pem", "student_public.pem", "add/student_public.pem"]
    public_key_path = find_public_key(possible_paths)
    if not public_key_path:
        print("Error: student_public.pem not found!")
        print("Searched paths:", possible_paths)
        sys.exit(1)

    # 2️⃣ Read public key
    with open(public_key_path, "r") as f:
        public_key = f.read().strip()
    public_key_json = public_key.replace("\n", "\\n")

    # 3️⃣ Prepare payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_json
    }

    print("\n--- Payload ---")
    print(json.dumps(payload, indent=2))

    # 4️⃣ Send POST request
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        data = response.json()
    except Exception as e:
        print("Error sending request or parsing response:", e)
        return

    print("\n--- API Response ---")
    print(data)

    # 5️⃣ Save encrypted seed
    if "encrypted_seed" in data:
        with open("encrypted_seed.txt", "w") as f:
            f.write(data["encrypted_seed"])
        print("\n✅ Encrypted seed saved to 'encrypted_seed.txt'")
    else:
        print("\nError: 'encrypted_seed' not found in response. Check student_id and repo URL.")

# -------- RUN HERE --------
student_id = "23A91A1252"
github_repo_url = "https://github.com/navya1129/TOTP-PROJECT"  # Must match exactly
request_seed(student_id, github_repo_url)
