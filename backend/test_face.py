# backend/test_face.py
from face_verification import FaceVerifier

# Test with images
verifier = FaceVerifier(threshold=0.6)

# Replace these with actual image paths
doc_image = "temp/test_document.jpg"  # Image with a face
selfie_image = "temp/test_selfie.jpg" # Selfie of the same person

result = verifier.verify_face(doc_image, selfie_image)

print("\n=== FACE VERIFICATION RESULT ===")
print(f"Success: {result.get('success')}")
print(f"Match Score: {result.get('match_score', 0)}%")
print(f"Is Match: {result.get('is_match', False)}")
print(f"Threshold: {result.get('threshold', 40)}%")
print(f"Confidence: {result.get('confidence', 'N/A')}")
print(f"Message: {result.get('message', 'N/A')}")
if not result.get('success'):
    print(f"Error: {result.get('error', 'Unknown error')}")