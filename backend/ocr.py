# backend/ocr.py
import re

print("Loading OCR module...")

try:
    import easyocr
    print("EasyOCR imported successfully. Creating reader...")
    reader = easyocr.Reader(['en'])
    print("EasyOCR reader created successfully!")
    
    def extract_text_from_image(image_path):
        print(f"OCR reading: {image_path}")
        try:
            result = reader.readtext(image_path, detail=0, paragraph=False)
            text = " ".join(result)
            print(f"OCR raw text: {text}")
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
            
except ImportError as e:
    print(f"EasyOCR not available: {e}")
    print("Using fallback mode.")
    
    def extract_text_from_image(image_path):
        print("Fallback OCR - returning empty text")
        return ""

def clean_name(raw_name):
    """Clean name by removing DOB and other unwanted text"""
    if not raw_name:
        return ""
    
    # Remove everything after "DOB" (case insensitive)
    cleaned = re.sub(r'\s*DOB\s+.*$', '', raw_name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*DOB$', '', cleaned, flags=re.IGNORECASE)
    
    # Remove "Date of Birth" and everything after
    cleaned = re.sub(r'\s*Date of Birth\s+.*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Date of Birth$', '', cleaned, flags=re.IGNORECASE)
    
    # Remove "Birth" and everything after
    cleaned = re.sub(r'\s*Birth\s+.*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Birth$', '', cleaned, flags=re.IGNORECASE)
    
    # Remove any numbers and special characters (keep letters, spaces, dots, hyphens)
    cleaned = re.sub(r'[^A-Za-z\s\.\-]', '', cleaned)
    
    # Remove extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def extract_fields_from_text(text):
    """Extract document fields from OCR text with proper cleaning"""
    fields = {}
    
    if not text:
        return fields
    
    print(f"Raw text: {text}")
    
    # First, clean the entire text to remove DOB patterns
    cleaned_text = re.sub(r'\s*DOB\s+\d{1,2}\s+[A-Za-z]+\s+\d{4}', '', text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\s*DOB$', '', cleaned_text, flags=re.IGNORECASE)
    print(f"Cleaned text: {cleaned_text}")
    
    # ==================== NAME EXTRACTION ====================
    name_patterns = [
        r'Name\s*[:.]?\s*([A-Za-z\s\.\-]+?)(?=\s+(?:DOB|Date of Birth|DOB:|Date:|$))',
        r'Name\s*[:.]?\s*([A-Za-z\s\.\-]+)',
        r'Full Name\s*[:.]?\s*([A-Za-z\s\.\-]+)',
        r'Given Name\s*[:.]?\s*([A-Za-z\s\.\-]+)',
        r'Surname\s*[:.]?\s*([A-Za-z\s\.\-]+)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            raw_name = match.group(1).strip()
            print(f"Raw name: '{raw_name}'")
            
            cleaned_name = clean_name(raw_name)
            
            if cleaned_name and len(cleaned_name) > 1:
                fields['name'] = cleaned_name
                print(f"✅ Cleaned name: '{fields['name']}'")
                break
    
    # If name not found, try looking for it after common labels
    if 'name' not in fields:
        name_match = re.search(r'([A-Za-z]+\s+[A-Za-z]+)(?=\s+DOB|\s+Date|\s+$)', cleaned_text, re.IGNORECASE)
        if name_match:
            raw_name = name_match.group(1).strip()
            fields['name'] = clean_name(raw_name)
            print(f"✅ Alternative name: '{fields.get('name', '')}'")
    
    # If still no name, try to extract any two-word name pattern
    if 'name' not in fields:
        name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', cleaned_text)
        if name_match:
            raw_name = name_match.group(1).strip()
            fields['name'] = clean_name(raw_name)
            print(f"✅ Pattern name: '{fields.get('name', '')}'")
    
    # ==================== DOCUMENT TYPE ====================
    text_lower = text.lower()
    if 'passport' in text_lower:
        fields['document_type'] = 'Passport'
    elif 'aadhaar' in text_lower or 'aadhar' in text_lower:
        fields['document_type'] = 'Aadhaar Card'
    elif 'driving license' in text_lower or 'driver' in text_lower:
        fields['document_type'] = 'Driving License'
    elif 'pan card' in text_lower:
        fields['document_type'] = 'PAN Card'
    elif 'visa' in text_lower:
        fields['document_type'] = 'Visa'
    elif 'id card' in text_lower or 'identity' in text_lower:
        fields['document_type'] = 'ID Card'
    else:
        fields['document_type'] = 'Unknown'
    print(f"Document type: {fields['document_type']}")
    
    # ==================== DOCUMENT NUMBER ====================
    num_patterns = [
        r'[Pp]assport\s*[Nn]o?\s*[:.]?\s*([A-Z0-9]+)',
        r'[Aa]adhaar\s*[Nn]umber\s*[:.]?\s*(\d{4}\s*\d{4}\s*\d{4})',
        r'[Dd]ocument\s*[Nn]umber\s*[:.]?\s*([A-Z0-9]+)',
        r'[Nn]umber\s*[:.]?\s*([A-Z0-9]+)',
        r'[Nn]o\s*[:.]?\s*([A-Z0-9]+)',
    ]
    for pattern in num_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields['document_number'] = match.group(1).strip()
            print(f"Document number: {fields['document_number']}")
            break
    
    # ==================== DATE OF BIRTH ====================
    dob_patterns = [
        r'DOB\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Date of Birth\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Birth\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Born\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields['dob'] = match.group(1).strip()
            print(f"DOB: {fields['dob']}")
            break
    
    # ==================== EXPIRY DATE ====================
    exp_patterns = [
        r'Expiry\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Expiration\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Valid Until\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Valid Through\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Valid Till\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'Expires\s*[:.]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields['expiry'] = match.group(1).strip()
            print(f"Expiry: {fields['expiry']}")
            break
    
    print(f"✅ Final extracted fields: {fields}")
    return fields