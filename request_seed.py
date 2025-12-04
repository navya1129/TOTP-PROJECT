import requests
import json
import sys

API_URL = "https://eajejyq4r3zjioq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed(student_id, github_repo_url):
    try:
        # 1. Read student public key
        with open("add/student_public.pem", "r") as f:
            public_key = f.read()

        # 2. Prepare JSON payload
        payload = {
            "student_id": student_id,
            "github_repo_url": github_repo_url,
            "public_key": public_key.replace("\n", "\\n")
        }

        # 3. Send POST request
        response = requests.post(API_URL, json=payload)

        # 4. Parse response
        data = response.json()
        print("Full API Response:", data)

        if "encrypted_seed" not in data:
            print("Error: 'encrypted_seed' not found in response. Check student ID, repo URL, and public key.")
            return

        encrypted_seed = data["encrypted_seed"]

        # 5. Save encrypted seed to file
        with open("encrypted_seed.txt", "w") as f:
            f.write(encrypted_seed)

        print("Encrypted seed saved to encrypted_seed.txt")

    except Exception as e:
        print("Error:", e)
        sys.exit(1)


# -------- RUN HERE --------
student_id = "23A91A1252"
github_repo_url = "https://github.com/navya1129/TOTP-PROJECT"

request_seed(student_id, github_repo_url)
