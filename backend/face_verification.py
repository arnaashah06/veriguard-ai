# backend/face_verification.py
"""
VeriGuard AI - Advanced Biometric Face Verification Engine
Computes 128D deep facial embeddings to verify identity consistency
between document portraits (Passports, Aadhaar, PAN, IDs) and selfies.
"""

import os
import sys
import math
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from PIL import Image, ImageOps

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# -----------------------------------------------------------------------------
# 1. Virtual Environment Auto-Resolution
# Ensures face_recognition, dlib, and cv2 are resolved even if executed
# from global Python or without manually activating the virtualenv.
# -----------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_candidate_sites = [
    os.path.join(_here, "venv", "Lib", "site-packages"),
    os.path.join(_here, "..", "backend", "venv", "Lib", "site-packages"),
    os.path.join(os.path.dirname(_here), "backend", "venv", "Lib", "site-packages"),
    r"C:\Users\pc\Desktop\veriguard-ai\backend\venv\Lib\site-packages",
]
for _site in _candidate_sites:
    if os.path.isdir(_site) and _site not in sys.path:
        sys.path.insert(0, _site)

# -----------------------------------------------------------------------------
# 2. Dependency Imports with Safe Fallbacks
# -----------------------------------------------------------------------------
import importlib

try:
    cv2 = importlib.import_module("cv2")
    HAS_CV2 = True
except Exception:
    cv2 = None
    HAS_CV2 = False

try:
    face_recognition = importlib.import_module("face_recognition")
    HAS_FACE_RECOGNITION = True
except Exception:
    face_recognition = None
    HAS_FACE_RECOGNITION = False


# -----------------------------------------------------------------------------
# 3. FaceVerifier Engine
# -----------------------------------------------------------------------------
class FaceVerifier:
    """
    Biometric Face Verification Engine.
    Compares cardholder portraits against live selfies with calibrated
    similarity scoring, multi-face resolution, and image quality checks.
    """

    def __init__(self, threshold: float = 0.60):
        """
        :param threshold: Strict Euclidean distance threshold (default 0.60).
                          Lower distance indicates higher biometric similarity.
        """
        self.threshold = float(threshold)

    # -------------------------------------------------------------------------
    # Image Loading & Preprocessing
    # -------------------------------------------------------------------------
    def _load_and_orient_image(self, image_path: str, max_dim: int = 1600) -> np.ndarray:
        """
        Loads an image, corrects EXIF orientation, converts to RGB, and scales down
        excessively large inputs while preserving aspect ratio.
        """
        with Image.open(image_path) as raw_img:
            img = ImageOps.exif_transpose(raw_img)
            img = img.convert("RGB")
            w, h = img.size
            if max(w, h) > max_dim:
                scale = max_dim / float(max(w, h))
                img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            return np.array(img)

    # -------------------------------------------------------------------------
    # Facial Quality Assessment
    # -------------------------------------------------------------------------
    def assess_face_quality(
        self, img_np: np.ndarray, face_box: Tuple[int, int, int, int]
    ) -> Dict[str, Any]:
        """
        Evaluates the detected face patch for blurriness, brightness, and resolution.
        """
        top, right, bottom, left = face_box
        h_img, w_img = img_np.shape[:2]
        top, bottom = max(0, min(top, h_img - 1)), max(top + 1, min(bottom, h_img))
        left, right = max(0, min(left, w_img - 1)), max(left + 1, min(right, w_img))

        face_chip = img_np[top:bottom, left:right]
        face_h, face_w = face_chip.shape[:2]

        if face_h < 2 or face_w < 2:
            return {"blur_score": 0.0, "is_blurry": True, "brightness": 0.0, "quality_grade": "POOR"}

        if HAS_CV2 and hasattr(cv2, "cvtColor") and hasattr(cv2, "Laplacian"):
            gray = cv2.cvtColor(face_chip, cv2.COLOR_RGB2GRAY)
            blur_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        else:
            gray = np.mean(face_chip, axis=2).astype(np.uint8)
            gy, gx = np.gradient(gray.astype(float))
            blur_var = float(np.var(np.sqrt(gx**2 + gy**2)) * 10.0)

        mean_brightness = float(np.mean(gray))
        is_blurry = bool(blur_var < 45.0)
        is_overexposed = bool(mean_brightness > 225)
        is_underexposed = bool(mean_brightness < 35)
        low_resolution = bool(face_w < 45 or face_h < 45)

        grade = "GOOD" if not (is_blurry or is_overexposed or is_underexposed or low_resolution) else "ACCEPTABLE"
        if is_blurry and (is_overexposed or is_underexposed or low_resolution):
            grade = "POOR"

        return {
            "blur_score": round(blur_var, 1),
            "is_blurry": is_blurry,
            "brightness": round(mean_brightness, 1),
            "is_overexposed": is_overexposed,
            "is_underexposed": is_underexposed,
            "width": int(face_w),
            "height": int(face_h),
            "quality_grade": grade,
        }

    # -------------------------------------------------------------------------
    # Face Detection & Encoding
    # -------------------------------------------------------------------------
    def detect_face_locations(
        self, img_np: np.ndarray
    ) -> Tuple[List[Tuple[int, int, int, int]], str]:
        """
        Locates face bounding boxes in an image.
        Uses primary HOG detector, with CLAHE contrast enhancement for dark/scanned IDs.
        """
        if not HAS_FACE_RECOGNITION:
            return [], "none"

        # 1. Standard HOG detector
        try:
            boxes = face_recognition.face_locations(img_np, number_of_times_to_upsample=1, model="hog")
            if boxes:
                return boxes, "hog_standard"
        except Exception:
            pass

        # 2. CLAHE contrast enhancement for low-contrast / laminated document photos
        if HAS_CV2 and hasattr(cv2, "createCLAHE") and hasattr(cv2, "cvtColor"):
            try:
                lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
                clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
                lab[:, :, 0] = clahe.apply(lab[:, :, 0])
                enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
                boxes = face_recognition.face_locations(enhanced, number_of_times_to_upsample=2, model="hog")
                if boxes:
                    return boxes, "clahe_enhanced_hog"
            except Exception:
                pass

        return [], "none"

    def _select_primary_face_box(
        self, face_locations: List[Tuple[int, int, int, int]], img_shape: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Selects the primary face box when multiple faces exist (e.g. ID card photo vs watermark).
        """
        if len(face_locations) == 1:
            return face_locations[0]

        img_h, img_w = img_shape[:2]
        center_x, center_y = img_w / 2.0, img_h / 2.0

        def box_score(box):
            top, right, bottom, left = box
            area = max(1, (bottom - top) * (right - left))
            dist = math.sqrt((((left + right) / 2.0 - center_x) / img_w) ** 2 + (((top + bottom) / 2.0 - center_y) / img_h) ** 2)
            return area * max(0.2, 1.0 - (dist * 0.5))

        return max(face_locations, key=box_score)

    def extract_face_encoding(
        self, image_path: str
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Locates faces in the given image path and returns the primary 128D encoding.
        Returns: (encoding, error_message)
        """
        if not HAS_FACE_RECOGNITION:
            return None, "Face recognition engine unavailable"

        try:
            img_np = self._load_and_orient_image(image_path)
        except Exception as e:
            return None, f"Failed to load image: {str(e)}"

        face_locations, _ = self.detect_face_locations(img_np)
        if not face_locations:
            return None, "No face detected in image"

        primary_box = self._select_primary_face_box(face_locations, img_np.shape)
        try:
            encodings = face_recognition.face_encodings(img_np, known_face_locations=[primary_box])
            if not encodings:
                return None, "Could not compute facial feature vector"
            return encodings[0], None
        except Exception as e:
            return None, f"Facial encoding computation failed: {str(e)}"

    def crop_face(
        self, image_path: str, output_path: Optional[str] = None, margin: float = 0.20
    ) -> Optional[Image.Image]:
        """
        Extracts the primary detected face with an expansion margin and returns the cropped Image.
        """
        try:
            img_np = self._load_and_orient_image(image_path)
            boxes, _ = self.detect_face_locations(img_np)
            if not boxes:
                return None

            primary_box = self._select_primary_face_box(boxes, img_np.shape)
            top, right, bottom, left = primary_box
            pad_h = int((bottom - top) * margin)
            pad_w = int((right - left) * margin)

            h_img, w_img = img_np.shape[:2]
            crop_top = max(0, top - pad_h)
            crop_bottom = min(h_img, bottom + pad_h)
            crop_left = max(0, left - pad_w)
            crop_right = min(w_img, right + pad_w)

            cropped_img = Image.fromarray(img_np[crop_top:crop_bottom, crop_left:crop_right])
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                cropped_img.save(output_path, "JPEG", quality=95)
            return cropped_img
        except Exception:
            return None

    # -------------------------------------------------------------------------
    # Biometric Similarity Scoring
    # -------------------------------------------------------------------------
    def compute_similarity(
        self, encoding1: np.ndarray, encoding2: np.ndarray
    ) -> Tuple[float, float, bool, str]:
        """
        Calculates calibrated similarity metrics from two 128D embeddings.
        Returns: (distance, match_score, is_match, confidence)
        """
        dist = float(face_recognition.face_distance([encoding1], encoding2)[0])

        if dist <= self.threshold:
            # Linear scaling from 100% (at dist=0) to 60% (at dist=threshold)
            match_score = (1.0 - (dist / self.threshold) * 0.40) * 100.0
        else:
            # Dropoff for non-matching faces
            excess = dist - self.threshold
            match_score = max(5.0, (0.60 - excess) / 0.60 * 60.0)

        match_score = min(99.9, max(5.0, round(match_score, 1)))
        is_match = bool(dist <= self.threshold)

        if dist <= 0.42:
            confidence = "HIGH"
        elif dist <= 0.58:
            confidence = "MEDIUM"
        elif dist <= 0.70:
            confidence = "LOW"
        else:
            confidence = "REJECT"

        return round(dist, 4), match_score, is_match, confidence

    # -------------------------------------------------------------------------
    # Full Verification Pipeline
    # -------------------------------------------------------------------------
    def verify_face(
        self, document_image_path: str, selfie_image_path: str
    ) -> Dict[str, Any]:
        """
        Compares face portrait on ID document against applicant selfie.
        Returns match verdict, calibrated score, confidence, and quality metrics.
        """
        print("\n" + "=" * 45)
        print("👤 RUNNING FACE VERIFICATION")
        print("=" * 45)
        print(f"Document Image: {document_image_path}")
        print(f"Selfie Image:   {selfie_image_path}")

        # 1. Path existence validation
        if not document_image_path or not os.path.exists(document_image_path):
            return {
                "success": False,
                "is_match": False,
                "match_score": 0,
                "threshold": round(self.threshold * 100, 1),
                "error": "Document image not found",
                "message": "⚠️ Document image file not found",
            }

        if not selfie_image_path or not os.path.exists(selfie_image_path):
            return {
                "success": False,
                "is_match": False,
                "match_score": 0,
                "threshold": round(self.threshold * 100, 1),
                "error": "Selfie image not found",
                "message": "ℹ️ Selfie image not provided for comparison",
            }

        if not HAS_FACE_RECOGNITION:
            return {
                "success": False,
                "is_match": False,
                "match_score": 0,
                "threshold": round(self.threshold * 100, 1),
                "error": "Face recognition engine unavailable",
                "message": "⚠️ Face recognition model not available",
            }

        try:
            # 2. Document face detection & encoding
            doc_img_np = self._load_and_orient_image(document_image_path)
            doc_boxes, doc_stage = self.detect_face_locations(doc_img_np)
            if not doc_boxes:
                print("[!] Document face extraction: No face detected in image")
                return {
                    "success": False,
                    "is_match": False,
                    "match_score": 0,
                    "threshold": 60.0,
                    "error": "No face detected in document image",
                    "message": "⚠️ No clear face detected in document image",
                }

            doc_primary_box = self._select_primary_face_box(doc_boxes, doc_img_np.shape)
            doc_quality = self.assess_face_quality(doc_img_np, doc_primary_box)
            doc_encodings = face_recognition.face_encodings(doc_img_np, known_face_locations=[doc_primary_box])
            if not doc_encodings:
                return {
                    "success": False,
                    "is_match": False,
                    "match_score": 0,
                    "threshold": 60.0,
                    "error": "Could not compute facial feature vector",
                    "message": "⚠️ No clear face detected in document image",
                }
            doc_encoding = doc_encodings[0]

            # 3. Selfie face detection & encoding
            selfie_img_np = self._load_and_orient_image(selfie_image_path)
            selfie_boxes, selfie_stage = self.detect_face_locations(selfie_img_np)
            if not selfie_boxes:
                print("[!] Selfie face extraction: No face detected in image")
                return {
                    "success": False,
                    "is_match": False,
                    "match_score": 0,
                    "threshold": 60.0,
                    "error": "No face detected in selfie image",
                    "message": "⚠️ No clear face detected in selfie image",
                }

            selfie_primary_box = self._select_primary_face_box(selfie_boxes, selfie_img_np.shape)
            selfie_quality = self.assess_face_quality(selfie_img_np, selfie_primary_box)
            selfie_encodings = face_recognition.face_encodings(selfie_img_np, known_face_locations=[selfie_primary_box])
            if not selfie_encodings:
                return {
                    "success": False,
                    "is_match": False,
                    "match_score": 0,
                    "threshold": 60.0,
                    "error": "Could not compute facial feature vector",
                    "message": "⚠️ No clear face detected in selfie image",
                }
            selfie_encoding = selfie_encodings[0]

            # 4. Biometric distance and similarity computation
            dist, match_score, is_match, confidence = self.compute_similarity(doc_encoding, selfie_encoding)

            # 5. Verdict messages
            if is_match:
                status_msg = f"✅ Face match verified ({match_score}% similarity)"
            else:
                status_msg = f"⚠️ Face mismatch - comparison score {match_score}% below threshold"

            print(f"[+] Distance: {dist:.4f} | Match Score: {match_score}% | Verified: {is_match}")
            print(f"[+] Verdict: {status_msg}")

            return {
                "success": True,
                "is_match": is_match,
                "match_score": match_score,
                "distance": dist,
                "threshold": 60.0,
                "confidence": confidence,
                "message": status_msg,
                "metrics": {
                    "doc_face_detected": True,
                    "selfie_face_detected": True,
                    "doc_detection_stage": doc_stage,
                    "selfie_detection_stage": selfie_stage,
                    "doc_face_count": len(doc_boxes),
                    "selfie_face_count": len(selfie_boxes),
                    "doc_face_box": {
                        "top": int(doc_primary_box[0]),
                        "right": int(doc_primary_box[1]),
                        "bottom": int(doc_primary_box[2]),
                        "left": int(doc_primary_box[3]),
                    },
                    "selfie_face_box": {
                        "top": int(selfie_primary_box[0]),
                        "right": int(selfie_primary_box[1]),
                        "bottom": int(selfie_primary_box[2]),
                        "left": int(selfie_primary_box[3]),
                    },
                    "doc_quality": doc_quality,
                    "selfie_quality": selfie_quality,
                },
            }

        except Exception as e:
            print(f"[!] Exception during face verification: {e}")
            return {
                "success": False,
                "is_match": False,
                "match_score": 0,
                "threshold": 60.0,
                "error": str(e),
                "message": f"⚠️ Face verification failed: {str(e)}",
            }


# -----------------------------------------------------------------------------
# Module Convenience Functions
# -----------------------------------------------------------------------------
_default_verifier: Optional[FaceVerifier] = None

def get_face_verifier(threshold: float = 0.60) -> FaceVerifier:
    """Returns a singleton or configured FaceVerifier instance."""
    global _default_verifier
    if _default_verifier is None or _default_verifier.threshold != threshold:
        _default_verifier = FaceVerifier(threshold=threshold)
    return _default_verifier


def verify_face(document_image_path: str, selfie_image_path: str, threshold: float = 0.60) -> Dict[str, Any]:
    """Functional convenience wrapper for FaceVerifier.verify_face."""
    verifier = get_face_verifier(threshold=threshold)
    return verifier.verify_face(document_image_path, selfie_image_path)