# backend/test_auth.py
from auth import (
    USERS_DB, verify_password, hash_password,
    create_access_token, decode_token
)

print("[TEST] Testing Password Hashing & Verification...")
stored_hash = USERS_DB["officer_compliance"]["password_hash"]
assert verify_password("Officer@2026", stored_hash) is True
assert verify_password("WrongPassword", stored_hash) is False
print("  -> Password hash & verify PASSED")

print("[TEST] Testing JWT Token Issuance & Decoding...")
token = create_access_token({"sub": "officer_compliance", "role": "compliance_officer"})
assert isinstance(token, str) and len(token) > 20

payload = decode_token(token)
assert payload is not None
assert payload.get("sub") == "officer_compliance"
assert payload.get("role") == "compliance_officer"
print("  -> JWT Issuance & Role Verification PASSED")
print("\n[ALL AUTH TESTS PASSED] [OK]")
