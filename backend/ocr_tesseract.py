# backend/ocr_tesseract.py
"""
VeriGuard AI - OCR and Document Field Extraction Engine
Powered by Tesseract OCR with multi-pass preprocessing and MRZ parsing.
"""

import os
import sys
import re
import datetime
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

# Ensure UTF-8 stdout encoding on Windows so logs/emojis never crash
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ==========================================
# CONFIGURE TESSERACT EXECUTABLE
# ==========================================

TESSERACT_CANDIDATE_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

def configure_tesseract():
    """Locate and configure Tesseract executable and tessdata path."""
    configured_path = None
    try:
        from tesseract_config import TESSERACT_PATH
        if os.path.isfile(TESSERACT_PATH):
            configured_path = TESSERACT_PATH
    except Exception:
        pass

    if not configured_path:
        for p in TESSERACT_CANDIDATE_PATHS:
            if os.path.isfile(p):
                configured_path = p
                break

    if configured_path:
        pytesseract.pytesseract.tesseract_cmd = configured_path
        tessdata_dir = os.path.join(os.path.dirname(configured_path), "tessdata")
        if os.path.isdir(tessdata_dir) and "TESSDATA_PREFIX" not in os.environ:
            os.environ["TESSDATA_PREFIX"] = tessdata_dir
        print(f"[*] Tesseract configured: {configured_path}")
        return True
    else:
        print("[!] Warning: Tesseract executable not found in standard paths.")
        return False

HAS_TESSERACT = configure_tesseract()


# ==========================================
# IMAGE PREPROCESSING
# ==========================================

def preprocess_image(image_path, mode="standard"):
    """
    Load image, transpose EXIF orientation, and apply optimal preprocessing.
    Uses context manager to prevent Windows file locking.
    """
    with Image.open(image_path) as raw_img:
        # Correct orientation from mobile phone cameras
        img = ImageOps.exif_transpose(raw_img)
        img = img.convert("RGB")

        # Resize small images to optimal OCR resolution (~1800-2400px width)
        width, height = img.size
        target_width = 2000
        if width < target_width:
            scale = target_width / float(width)
            new_size = (target_width, int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        elif width > 3500:
            scale = 3000 / float(width)
            new_size = (3000, int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Convert to Grayscale
        gray = img.convert("L")

        if mode == "high_contrast":
            # Extra contrast for faint documents
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            enhanced = enhanced.filter(ImageFilter.SHARPEN)
            return enhanced
        else:
            # Standard enhancement
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(1.6)
            brightness = ImageEnhance.Brightness(enhanced)
            enhanced = brightness.enhance(1.05)
            enhanced = enhanced.filter(ImageFilter.SHARPEN)
            return enhanced


# ==========================================
# OCR TEXT EXTRACTION
# ==========================================

def extract_text_from_image(image_path):
    """
    Extract raw text using Tesseract OCR with multi-pass fallback.
    """
    if not os.path.exists(image_path):
        print(f"[!] Error: Image path does not exist: {image_path}")
        return ""

    if not HAS_TESSERACT:
        print("[!] Tesseract is not available.")
        return ""

    try:
        # Pass 1: Standard preprocessing with Automatic Page Segmentation (PSM 3)
        img_prep1 = preprocess_image(image_path, mode="standard")
        text = pytesseract.image_to_string(
            img_prep1,
            lang="eng",
            config="--oem 3 --psm 3"
        ).strip()

        # Pass 2 fallback: If text length is too small, try PSM 6 with high contrast
        if len(text) < 40:
            img_prep2 = preprocess_image(image_path, mode="high_contrast")
            alt_text = pytesseract.image_to_string(
                img_prep2,
                lang="eng",
                config="--oem 3 --psm 6"
            ).strip()
            if len(alt_text) > len(text):
                text = alt_text

        # Pass 3: Multi-pass sparse text scan (PSM 11) for documents with isolated headers or numbers
        if len(text) < 150 or not re.search(r"(?:\d{4}|P<|passport|aadhaar|pan)", text, re.IGNORECASE):
            try:
                with Image.open(image_path) as raw_im:
                    raw_im = ImageOps.exif_transpose(raw_im).convert("RGB")
                    sparse_text = pytesseract.image_to_string(
                        raw_im,
                        lang="eng",
                        config="--oem 3 --psm 11"
                    ).strip()
                    if sparse_text and len(sparse_text) > 10:
                        text = (text + "\n" + sparse_text).strip()
            except Exception:
                pass

        print(f"[+] OCR extracted {len(text)} characters")
        return text

    except Exception as e:
        print(f"[!] Tesseract OCR Error: {e}")
        return ""


# ==========================================
# MRZ (MACHINE READABLE ZONE) PARSER
# ==========================================

def parse_mrz(text):
    """
    Detect and parse standard ICAO 9303 TD3 (2-line passport) MRZ.
    Line 1: P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<< (44 chars)
    Line 2: L898902C36UTO7408122F1204159ZE184226B<<<<<10 (44 chars)
    """
    lines = [line.strip().replace(" ", "").upper() for line in text.splitlines() if len(line.strip()) >= 30]
    mrz_lines = []
    
    for line in lines:
        clean = re.sub(r"[^A-Z0-9<]", "", line)
        if len(clean) >= 36 and "<<" in clean:
            mrz_lines.append(clean)
        elif len(clean) >= 36 and (clean.startswith("P<") or clean.startswith("P")):
            mrz_lines.append(clean)

    if len(mrz_lines) < 2:
        return None

    line1 = mrz_lines[-2]
    line2 = mrz_lines[-1]

    parsed = {
        "mrz_line1": line1,
        "mrz_line2": line2
    }

    try:
        # Line 1: P<ISSLASTNAME<<FIRSTNAME<MID<<<<...
        if line1.startswith("P"):
            parsed["document_type"] = "Passport"
            issuing_country = line1[2:5].replace("<", "")
            if issuing_country:
                parsed["country"] = issuing_country

            names_part = line1[5:]
            # Trim trailing filler padding
            if "<<" in names_part:
                parts = names_part.split("<<")
                surname = parts[0].replace("<", " ").strip()
                given_raw = parts[1] if len(parts) > 1 else ""
                # ICAO 9303 uses single '<' between multiple given names and '<<' or more for trailing fillers
                given_core = re.split(r"<<+", given_raw)[0]
                given_names = given_core.rstrip("<").replace("<", " ").strip()
                full_name = f"{given_names} {surname}".strip()
                if full_name:
                    parsed["name"] = full_name
            else:
                # No standard '<<' separator
                raw_cand = re.split(r"<+", names_part)[0].strip()
                parsed["name"] = raw_cand or names_part.replace("<", " ").strip()

        # Line 2: DocNumber(9) + CheckDigit(1) + Nationality(3) + DOB(6) + Check(1) + Sex(1) + Expiry(6)
        if len(line2) >= 28:
            doc_num_raw = line2[0:9].replace("<", "").strip()
            if doc_num_raw:
                parsed["document_number"] = doc_num_raw

            # Nationality: positions 10..12
            if len(line2) >= 13:
                nationality = line2[10:13].replace("<", "").strip()
                if nationality:
                    parsed["nationality"] = nationality

            # DOB: YYMMDD
            dob_raw = line2[13:19]
            if dob_raw.isdigit() and len(dob_raw) == 6:
                yy = int(dob_raw[0:2])
                mm = int(dob_raw[2:4])
                dd = int(dob_raw[4:6])
                curr_yy = datetime.datetime.now().year % 100
                century = 1900 if yy > curr_yy else 2000
                year = century + yy
                if 1 <= mm <= 12 and 1 <= dd <= 31:
                    parsed["dob"] = f"{dd:02d}/{mm:02d}/{year}"

            # Expiry: YYMMDD
            exp_raw = line2[21:27]
            if exp_raw.isdigit() and len(exp_raw) == 6:
                yy = int(exp_raw[0:2])
                mm = int(exp_raw[2:4])
                dd = int(exp_raw[4:6])
                year = 2000 + yy
                if 1 <= mm <= 12 and 1 <= dd <= 31:
                    parsed["expiry"] = f"{dd:02d}/{mm:02d}/{year}"

        if parsed.get("name") or parsed.get("document_number"):
            return parsed
    except Exception as e:
        print(f"[!] MRZ parsing note: {e}")

    return None


# ==========================================
# FIELD EXTRACTION LOGIC
# ==========================================

def clean_text(value):
    """Normalize whitespace and remove non-printable characters."""
    if not value:
        return ""
    value = re.sub(r"\s+", " ", value)
    return value.strip()

def clean_extracted_name(raw_name):
    """Clean name by stripping field labels and irrelevant tokens."""
    if not raw_name:
        return ""
    stop_words = (
        r"\b(?:DOB|Date of Birth|Birth|Expiry|Expiration|Expires|Passport|Number|Document|Nationality|Sex|Gender|Signature)\b.*$"
    )
    name = re.sub(stop_words, "", raw_name, flags=re.IGNORECASE)
    name = re.sub(r"^(?:Name|Full Name|Given Name|Surname|Nom|Pr[ée]noms?)\s*[:\-]?\s*", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[^A-Za-z \-\']", "", name)
    name = clean_text(name)
    return name

MONTHS_MAP = {
    'jan': '01', 'january': '01',
    'feb': '02', 'february': '02',
    'mar': '03', 'march': '03',
    'apr': '04', 'april': '04',
    'may': '05',
    'jun': '06', 'june': '06',
    'jul': '07', 'july': '07',
    'aug': '08', 'august': '08',
    'sep': '09', 'sept': '09', 'september': '09',
    'oct': '10', 'october': '10',
    'nov': '11', 'november': '11',
    'dec': '12', 'december': '12',
}

def normalize_date(date_str):
    """Normalize extracted date string to DD/MM/YYYY format."""
    if not date_str:
        return None
    date_str = clean_text(date_str)

    # DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    m = re.match(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})$", date_str)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            curr_yy = datetime.datetime.now().year % 100
            y += 2000 if y <= curr_yy else 1900
        if 1 <= d <= 31 and 1 <= mo <= 12:
            return f"{d:02d}/{mo:02d}/{y}"

    # YYYY/MM/DD or YYYY-MM-DD
    m = re.match(r"^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$", date_str)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= d <= 31 and 1 <= mo <= 12:
            return f"{d:02d}/{mo:02d}/{y}"

    # DD Month YYYY (e.g. 15 Jan 1990)
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{2,4})$", date_str)
    if m:
        d = int(m.group(1))
        mo_str = m.group(2).lower()
        y = int(m.group(3))
        if y < 100:
            y += 1900 if y > 30 else 2000
        if mo_str in MONTHS_MAP and 1 <= d <= 31:
            return f"{d:02d}/{MONTHS_MAP[mo_str]}/{y}"

    # Month DD, YYYY (e.g. Jan 15, 1990)
    m = re.match(r"^([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{2,4})$", date_str)
    if m:
        mo_str = m.group(1).lower()
        d = int(m.group(2))
        y = int(m.group(3))
        if mo_str in MONTHS_MAP and 1 <= d <= 31:
            return f"{d:02d}/{MONTHS_MAP[mo_str]}/{y}"

    return date_str


def extract_fields_from_text(text):
    """
    Extract structured document fields:
    - document_type (Passport, Aadhaar Card, PAN Card, Driving License, ID Card, Unknown)
    - name
    - dob
    - expiry
    - document_number
    """
    fields = {}
    if not text:
        return fields

    lines = [clean_text(l) for l in text.splitlines() if clean_text(l)]
    full_text_single = " ".join(lines)
    lower_text = full_text_single.lower()

    # 1. First, attempt MRZ extraction (highest precision for passports)
    mrz_data = parse_mrz(text)
    if mrz_data:
        fields.update(mrz_data)
        print(f"[+] MRZ parsed: {mrz_data}")

    # 2. Document Type Detection
    if "document_type" not in fields:
        if "passport" in lower_text or "p<" in text:
            fields["document_type"] = "Passport"
        elif "aadhaar" in lower_text or "aadhar" in lower_text or "unique identification" in lower_text or "government of india" in lower_text or re.search(r"\b[X\*\.]{4}\s+[X\*\.]{4}\s+\d{4}\b", full_text_single, re.IGNORECASE) or re.search(r"\b\d{4}\s+\d{4}\s+\d{4}\b", full_text_single):
            fields["document_type"] = "Aadhaar Card"
        elif "permanent account number" in lower_text or "pan card" in lower_text or "income tax department" in lower_text:
            fields["document_type"] = "PAN Card"
        elif "driving licence" in lower_text or "driving license" in lower_text or "driver license" in lower_text:
            fields["document_type"] = "Driving License"
        elif "voter" in lower_text or "election commission" in lower_text or "elector photo" in lower_text or "epic" in lower_text:
            fields["document_type"] = "Voter ID"
        elif "visa" in lower_text:
            fields["document_type"] = "Visa"
        elif "identity card" in lower_text or "national id" in lower_text or "id card" in lower_text:
            fields["document_type"] = "ID Card"
        else:
            fields["document_type"] = "Unknown"

    # 3. Name Extraction (if not obtained from MRZ)
    if not fields.get("name"):
        name_patterns = [
            r"(?:Full\s+Name|Given\s+Name|Surname|Name|Nom|Pr[ée]noms?)\s*[:\-]?\s*([A-Za-z\s.\'-]{2,40})",
            r"(?:Holder\s+Name|Cardholder\s+Name)\s*[:\-]?\s*([A-Za-z\s.\'-]{2,40})",
        ]
        for pattern in name_patterns:
            for line in lines:
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    cand = clean_extracted_name(m.group(1))
                    if cand and len(cand) >= 3 and cand.lower() not in ["passport", "republic", "government", "signature", "india"]:
                        fields["name"] = cand
                        break
            if fields.get("name"):
                break

        # Fallback for documents without explicit label (e.g. Aadhaar Card where name is line above DOB)
        if not fields.get("name"):
            for idx, line in enumerate(lines):
                if re.search(r"\b(?:DOB|Date of Birth|Birth|Year of Birth)\b", line, re.IGNORECASE):
                    if idx > 0:
                        prev_line = clean_extracted_name(lines[idx - 1])
                        if prev_line and len(prev_line) >= 3 and not any(k in prev_line.lower() for k in ["government", "india", "male", "female"]):
                            fields["name"] = prev_line
                            break

    # 4. Date of Birth (DOB) Extraction
    if not fields.get("dob"):
        dob_patterns = [
            r"\b(?:DOB|Date\s+of\s+Birth|Birth\s*Date|D\.O\.B\.|Born)\s*[:\-]?\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})",
            r"\b(?:DOB|Date\s+of\s+Birth|Birth\s*Date|D\.O\.B\.|Born)\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})",
            r"\b(?:DOB|Date\s+of\s+Birth|Birth\s*Date|D\.O\.B\.|Born)\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4})",
            r"\b(?:Year\s+of\s+Birth|YOB)\s*[:\-]?\s*(\d{4})",
        ]
        for pattern in dob_patterns:
            m = re.search(pattern, full_text_single, re.IGNORECASE)
            if m:
                raw_d = m.group(1)
                norm = normalize_date(raw_d)
                if norm:
                    fields["dob"] = norm
                    break

    # 5. Expiry Date Extraction
    if not fields.get("expiry"):
        expiry_patterns = [
            r"\b(?:Expiry|Expiration|Expires?|Valid\s+Until|Valid\s+Till|Valid\s+Through|Date\s+of\s+Expiry)\s*(?:Date)?\s*[:\-]?\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})",
            r"\b(?:Expiry|Expiration|Expires?|Valid\s+Until|Valid\s+Till|Valid\s+Through|Date\s+of\s+Expiry)\s*(?:Date)?\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})",
            r"\b(?:Expiry|Expiration|Expires?|Valid\s+Until|Valid\s+Till|Valid\s+Through|Date\s+of\s+Expiry)\s*(?:Date)?\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4})",
        ]
        for pattern in expiry_patterns:
            m = re.search(pattern, full_text_single, re.IGNORECASE)
            if m:
                raw_d = m.group(1)
                norm = normalize_date(raw_d)
                if norm:
                    fields["expiry"] = norm
                    break

    # 6. Document Number Extraction
    if not fields.get("document_number"):
        doc_type = fields.get("document_type", "Unknown")

        # Aadhaar Card: 12 digits or Masked (XXXX XXXX 1234)
        if doc_type == "Aadhaar Card" or "aadhaar" in lower_text:
            m_masked = re.search(r"\b([X\*\.]{4}\s+[X\*\.]{4}\s+\d{4})\b", full_text_single, re.IGNORECASE)
            if m_masked:
                fields["document_number"] = m_masked.group(1).upper()
            else:
                m = re.search(r"\b(\d{4}\s+\d{4}\s+\d{4})\b", full_text_single)
                if m:
                    fields["document_number"] = m.group(1).strip()

        # PAN Card: 5 uppercase letters, 4 digits, 1 uppercase letter (e.g. ABCDE1234F)
        if not fields.get("document_number") and (doc_type == "PAN Card" or "pan" in lower_text):
            m = re.search(r"\b([A-Z]{5}\d{4}[A-Z])\b", full_text_single)
            if m:
                fields["document_number"] = m.group(1)

        # Passport: 1 letter + 7-8 digits (e.g. A1234567) or generic 7-9 alphanumeric
        if not fields.get("document_number") and doc_type == "Passport":
            m = re.search(r"\b(?:Passport\s*(?:No\.?|Number)?)\s*[:#\-]?\s*([A-Z0-9]{7,9})\b", full_text_single, re.IGNORECASE)
            if m:
                fields["document_number"] = m.group(1).upper()

        # Driving License: DL followed by state code and numbers
        if not fields.get("document_number") and (doc_type == "Driving License" or "driving" in lower_text):
            m = re.search(r"\b(?:DL\s*(?:No\.?|Number)?|Licence\s*No\.?)\s*[:#\-]?\s*([A-Z0-9\- ]{8,20})\b", full_text_single, re.IGNORECASE)
            if m:
                fields["document_number"] = clean_text(m.group(1)).upper()

        # Voter ID (EPIC): 3 uppercase letters followed by 7 digits (e.g. ABC1234567)
        if not fields.get("document_number") and (doc_type in ["Voter ID", "ID Card"] or "voter" in lower_text or "epic" in lower_text or "election commission" in lower_text):
            m = re.search(r"\b([A-Z]{3}[0-9]{7})\b", full_text_single)
            if m:
                fields["document_number"] = m.group(1).upper()

        # Generic Document / ID Number pattern fallback
        if not fields.get("document_number"):
            generic_patterns = [
                r"\b(?:Document|ID|Identity|Certificate)\s*(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9\-]{6,20})\b",
                r"\b(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9]{7,15})\b",
            ]
            for pat in generic_patterns:
                m = re.search(pat, full_text_single, re.IGNORECASE)
                if m:
                    cand = m.group(1).upper().strip()
                    if cand not in ["PASSPORT", "DOCUMENT", "NUMBER", "IDENTITY"]:
                        fields["document_number"] = cand
                        break

    # Standardize missing fields to empty or reasonable fallbacks
    fields.setdefault("name", "Not detected")
    fields.setdefault("document_type", "Unknown")
    fields.setdefault("document_number", "Not detected")
    fields.setdefault("dob", "Not detected")
    fields.setdefault("expiry", "Not detected")

    print("[+] Extracted Document Fields:")
    for k, v in fields.items():
        print(f"    - {k}: {v}")

    return fields