# backend/test_forensics.py
from forensics import TamperingDetector

# Test with an actual image
image_path = "temp/your_image.png"  # Change to your image path

print("=== TESTING TAMPERING DETECTION ===")
detector = TamperingDetector(image_path)
results = detector.analyze_all()

print(f"\nSignals found: {len(results)}")
for signal in results:
    print(f"- {signal['type']}: {signal['severity']}")
    print(f"  {signal['details']}")

report = detector.get_report()
print(f"\nOverall: {report['overall_suspicion']}")