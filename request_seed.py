import requests
import json
import sys
import base64

API_URL = "https://eajejyq4r3zjioq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed(student_id, github_repo_url):
    try:
        # 1. Read student public key as bytes
        with open("app/student_public.pem", "rb") as f:
            public_key = f.read()

        # 2. Convert bytes to base64 string (safe for JSON)
        public_key_b64 = base64.b64encode(public_key).decode('utf-8')

        # 3. Prepare JSON payload
        payload = {
            "student_id": student_id,
            "github_repo_url": github_repo_url,
            "public_key": public_key_b64
        }

        # --- DEBUG: print payload before sending ---
        print("\n--- Payload being sent ---")
        print(json.dumps(payload, indent=2))

        # 4. Send POST request
        response = requests.post(API_URL, json=payload)

        # 5. Parse and print response
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("\nError: Response is not valid JSON")
            print("Raw Response:", response.text)
            return

        print("\n--- Full API Response ---")
        print(data)

        # 6. Check for encrypted_seed
        if "encrypted_seed" not in data:
            print("\nError: 'encrypted_seed' not found in response.")
            print("Suggestions:")
            print(" - Check that your student ID is correct and matches server records.")
            print(" - Check that the GitHub repo URL is exactly what the server expects.")
            print(" - Ensure your public key is registered with the server (if required).")
            print(" - If you recently changed keys or repo, try re-registering them.")
            return

        # 7. Save encrypted seed to file
        encrypted_seed = data["encrypted_seed"]
        with open("encrypted_seed.txt", "w") as f:
            f.write(encrypted_seed)

        print("\nEncrypted seed saved to 'encrypted_seed.txt' successfully!")

    except FileNotFoundError:
        print("Error: student_public.pem file not found in 'app/' folder")
        sys.exit(1)
    except Exception as e:
        print("Unexpected Error:", e)
        sys.exit(1)


# -------- RUN HERE --------
student_id = "23A91A1252"
github_repo_url = "https://github.com/navya1129/TOTP-PROJECT"

request_seed(student_id, github_repo_url)
