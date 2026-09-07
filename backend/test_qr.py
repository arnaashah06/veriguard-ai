# backend/test_qr.py
from aadhaar_qr import aadhaar_qr_verifier

xml = '<PrintLetterBarcodeData uid="123456789012" name="Priya Patel" gender="F" yob="1992" dist="Ahmedabad" state="Gujarat" pc="380015"/>'
res = aadhaar_qr_verifier.decode_qr_payload(xml)
print("Aadhaar QR Decoded:", res.get("valid"), "| Name:", res.get("name"), "| Cryptographic Sig:", res.get("cryptographic_signature_verified"))
assert res.get("valid") is True
assert res.get("name") == "Priya Patel"
print("Aadhaar QR Test Passed Successfully! [OK]")
