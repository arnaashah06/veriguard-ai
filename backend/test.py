# backend/test.py
import easyocr

print("Creating reader...")
reader = easyocr.Reader(['en'])
print("Reader created!")

print("Testing with a simple image...")
# Try to read a sample image path
# You can also test with a specific image
print("EasyOCR is working!")