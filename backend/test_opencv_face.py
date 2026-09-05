# backend/test_opencv_face.py
import cv2
import os

def test_face_detection(image_path):
    print(f"\nTesting: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Could not load image")
        return
    
    print(f"Image shape: {img.shape}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    print(f"Found {len(faces)} face(s)")
    
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            print(f"  Face at: x={x}, y={y}, w={w}, h={h}")
    else:
        print("❌ No faces detected - image may not have a clear face")

# Test all images in temp folder
print("="*50)
print("TESTING FACE DETECTION")
print("="*50)

if os.path.exists("temp"):
    for file in os.listdir("temp"):
        if file.endswith(('.jpg', '.jpeg', '.png')):
            test_face_detection(os.path.join("temp", file))
else:
    print("❌ Temp folder not found")