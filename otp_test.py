import pyotp

# 1. Create a secret key (store this somewhere safe)
secret_key = pyotp.random_base32()
print("Your secret key:", secret_key)

# 2. Create a TOTP object
totp = pyotp.TOTP(secret_key)

# 3. Generate current OTP
otp = totp.now()
print("Your OTP:", otp)

# 4. Verify OTP (optional)
user_input = input("Enter the OTP to verify: ")

if totp.verify(user_input):
    print("OTP Verified Successfully!")
else:
    print("Invalid OTP!")
