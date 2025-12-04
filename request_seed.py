import requests
import json
import sys
import os

API_URL = "https://eajejyq4r3zjioq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def find_public_key(possible_paths):
    """Find student_public.pem in multiple folders"""
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def request_seed(student_id, github_repo_url, api_url=API_URL):
    try:
        # 1. Find public key
        possible_paths = ["app/student_public.pem", "add/student_public.pem"]
        public_key_path = find_public_key(possible_paths)
        if not public_key_path:
            print("Error: student_public.pem file not found in any of the expected folders:")
            print(possible_paths)
            sys.exit(1)

        # 2. Read public key as text and convert line breaks to \n
        with open(public_key_path, "r") as f:
            public_key = f.read().strip()
        public_key_json = public_key.replace("\n", "\\n")

        # 3. Prepare JSON payload
        payload = {
            "student_id": student_id,
            "github_repo_url": github_repo_url,
            "public_key": public_key_json
        }

        print("\n--- Payload being sent ---")
        print(json.dumps(payload, indent=2))

        # 4. Send POST request
        response = requests.post(api_url, json=payload, timeout=10)

        # 5. Parse response
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON")
            print("Raw Response:", response.text)
            return

        print("\n--- Full API Response ---")
        print(data)

        if "encrypted_seed" not in data:
            print("\nError: 'encrypted_seed' not found in response.")
            print("Suggestions:")
            print(" - Ensure student_id matches exactly")
            print(" - Use the exact GitHub repo URL you will submit")
            print(" - Ensure your public key is registered if required")
            return

        # 6. Save encrypted seed
        with open("encrypted_seed.txt", "w") as f:
            f.write(data["encrypted_seed"])

        print("\nEncrypted seed saved to 'encrypted_seed.txt' successfully!")

    except Exception as e:
        print("Unexpected Error:", e)
        sys.exit(1)


# -------- RUN HERE --------
student_id = "23A91A1252"
github_repo_url = "https://github.com/navya1129/TOTP-PROJECT"  # Use exact URL you will submit

request_seed(student_id, github_repo_url)
