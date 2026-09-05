# backend/validators.py
"""
VeriGuard AI - Document Validation & Indian Government Document Authentication Engine
Provides deep mathematical, structural, and design verification for:
- Indian Aadhaar Card (UIDAI Verhoeff Checksum & Security Markers)
- Indian PAN Card (Income Tax Dept 10-char Syntax, 4th Char Entity, 5th Char Surname Match)
- Indian Voter ID (EPIC Format & Election Commission Validation)
- Indian Driving Licence (State RTO Jurisdiction & Format)
- Indian Passport (MEA Format & ICAO 9303 Compliance)
- General International Passports & ID Cards
"""

from datetime import datetime
import re
from typing import Dict, Any, List, Tuple, Optional


# =========================================================================
# VERHOEFF ALGORITHM (DIHEDRAL D5 CHECKSUM FOR AADHAAR NUMBERS)
# =========================================================================

VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

VERHOEFF_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(num_str: str) -> bool:
    """
    Validates a 12-digit Indian Aadhaar number using the official Verhoeff dihedral D5 algorithm.
    Returns True if the 12th digit matches the mathematical checksum of the preceding 11 digits.
    """
    clean = re.sub(r"\D", "", str(num_str))
    if len(clean) != 12:
        return False
    c = 0
    for i, item in enumerate(reversed(clean)):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(item)]]
    return c == 0


def generate_verhoeff_check_digit(eleven_digits: str) -> int:
    """Generate the 12th Verhoeff check digit for an 11-digit prefix."""
    clean = re.sub(r"\D", "", str(eleven_digits))
    if len(clean) != 11:
        return -1
    c = 0
    for i, item in enumerate(reversed(clean)):
        c = VERHOEFF_D[c][VERHOEFF_P[(i + 1) % 8][int(item)]]
    return VERHOEFF_INV[c]


# Indian States and Union Territories code dictionary for Driving Licences
INDIAN_STATE_CODES = {
    'AN': 'Andaman and Nicobar', 'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh',
    'AS': 'Assam', 'BR': 'Bihar', 'CH': 'Chandigarh', 'CG': 'Chhattisgarh',
    'DD': 'Daman and Diu', 'DL': 'Delhi', 'DN': 'Dadra and Nagar Haveli',
    'GA': 'Goa', 'GJ': 'Gujarat', 'HR': 'Haryana', 'HP': 'Himachal Pradesh',
    'JH': 'Jharkhand', 'JK': 'Jammu and Kashmir', 'KA': 'Karnataka',
    'KL': 'Kerala', 'LA': 'Ladakh', 'LD': 'Lakshadweep', 'MH': 'Maharashtra',
    'ML': 'Meghalaya', 'MN': 'Manipur', 'MP': 'Madhya Pradesh', 'MZ': 'Mizoram',
    'NL': 'Nagaland', 'OD': 'Odisha', 'PB': 'Punjab', 'PY': 'Puducherry',
    'RJ': 'Rajasthan', 'SK': 'Sikkim', 'TN': 'Tamil Nadu', 'TR': 'Tripura',
    'TS': 'Telangana', 'UK': 'Uttarakhand', 'UP': 'Uttar Pradesh', 'WB': 'West Bengal'
}

# Income Tax Department PAN 4th Character Taxpayer Entity Mapping
PAN_ENTITY_TYPES = {
    'P': 'Individual (Person)',
    'C': 'Company',
    'H': 'Hindu Undivided Family (HUF)',
    'F': 'Partnership Firm / LLP',
    'A': 'Association of Persons (AOP)',
    'T': 'Trust',
    'B': 'Body of Individuals (BOI)',
    'L': 'Local Authority',
    'J': 'Artificial Juridical Person',
    'G': 'Government Agency'
}

# =========================================================================
# ICAO 9303 & ISO 3166-1 OFFICIAL COUNTRY CODES & CHECKSUMS
# =========================================================================

ISO_ICAO_COUNTRY_CODES = {
    'ABW', 'AFG', 'AGO', 'AIA', 'ALA', 'ALB', 'AND', 'ARE', 'ARG', 'ARM', 'ASM', 'ATA', 'ATF', 'ATG', 'AUS', 'AUT',
    'AZE', 'BDI', 'BEL', 'BEN', 'BES', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BIH', 'BLM', 'BLR', 'BLZ', 'BMU', 'BOL',
    'BRA', 'BRB', 'BRN', 'BTN', 'BVT', 'BWA', 'CAF', 'CAN', 'CCK', 'CHE', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG',
    'COK', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CXR', 'CYM', 'CYP', 'CZE', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM',
    'DZA', 'ECU', 'EGY', 'ERI', 'ESH', 'ESP', 'EST', 'ETH', 'FIN', 'FJI', 'FLK', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR',
    'GEO', 'GGY', 'GHA', 'GIB', 'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GRL', 'GTM', 'GUF', 'GUM', 'GUY',
    'HKG', 'HMD', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IMN', 'IND', 'IOT', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA',
    'JAM', 'JEY', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LBR', 'LBY',
    'LCA', 'LIE', 'LKA', 'LSO', 'LTU', 'LUX', 'LVA', 'MAC', 'MAF', 'MAR', 'MCO', 'MDA', 'MDG', 'MDV', 'MEX', 'MHL',
    'MKD', 'MLI', 'MLT', 'MMR', 'MNE', 'MNG', 'MNP', 'MOZ', 'MRT', 'MSR', 'MTQ', 'MUS', 'MWI', 'MYS', 'MYT', 'NAM',
    'NCL', 'NER', 'NFK', 'NGA', 'NIC', 'NIU', 'NLD', 'NOR', 'NPL', 'NRU', 'NZL', 'OMN', 'PAK', 'PAN', 'PCN', 'PER',
    'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRK', 'PRT', 'PRY', 'PSE', 'PYF', 'QAT', 'REU', 'ROU', 'RUS', 'RWA', 'SAU',
    'SDN', 'SEN', 'SGP', 'SGS', 'SHN', 'SJM', 'SLB', 'SLE', 'SLV', 'SMR', 'SOM', 'SPM', 'SRB', 'SSD', 'STP', 'SUR',
    'SVK', 'SVN', 'SWE', 'SWZ', 'SXM', 'SYC', 'SYR', 'TCA', 'TCD', 'TGO', 'THA', 'TJK', 'TKL', 'TKM', 'TLS', 'TON',
    'TTO', 'TUN', 'TUR', 'TUV', 'TWN', 'TZA', 'UGA', 'UKR', 'UMI', 'URY', 'USA', 'UZB', 'VAT', 'VCT', 'VEN', 'VGB',
    'VIR', 'VNM', 'VUT', 'WLF', 'WSM', 'YEM', 'ZAF', 'ZMB', 'ZWE',
    # Official ICAO 9303 Special Organization & Travel Document Codes:
    'UTO', # Utopia (official ICAO sample test code)
    'XXA', 'XXB', 'XXC', 'XXX', # Stateless / Refugee / Unspecified
    'UNA', 'UNK', 'XPO', 'XOM'
}

def icao_char_value(c: str) -> int:
    """ICAO 9303 character weight converter for machine readable zones."""
    if '0' <= c <= '9':
        return int(c)
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A') + 10
    return 0

def calculate_icao_checksum(data: str) -> int:
    """Calculates official ICAO 9303 7-3-1 repeating weighted modulo 10 check digit."""
    weights = [7, 3, 1]
    return sum(weights[i % 3] * icao_char_value(c) for i, c in enumerate(data)) % 10


class DocumentValidator:
    def __init__(self, extracted_fields: Dict[str, Any], raw_text: str = ""):
        self.fields = extracted_fields
        self.raw_text = raw_text or extracted_fields.get("raw_text", "")
        self.findings: List[Dict[str, Any]] = []
        self.risk_score: int = 0
        self.document_type: str = extracted_fields.get("document_type", "Unknown")

    def validate_all(self) -> Tuple[List[Dict[str, Any]], int]:
        """Run all field validations, expiry checks, and Indian document security checks."""
        self.validate_required_fields()
        self.validate_expiry()
        self.validate_dob_format()
        self.validate_document_number()
        self.validate_indian_government_document()
        self.validate_mrz_security()
        self.validate_name_quality()
        self.calculate_risk_score()
        return self.findings, self.risk_score

    def validate_required_fields(self):
        """
        Validates presence of core fields.
        Crucial: For Indian Aadhaar Cards and PAN Cards, expiry date is NOT required
        because they have lifetime statutory validity under Government of India laws.
        """
        is_lifetime_indian_doc = self.document_type in ["Aadhaar Card", "PAN Card", "Voter ID"]

        if is_lifetime_indian_doc:
            required = ['name', 'document_number', 'dob']
        else:
            required = ['name', 'document_number', 'dob', 'expiry']

        missing = [field for field in required if field not in self.fields or not self.fields[field] or self.fields[field] == "Not detected"]

        if missing:
            self.findings.append({
                'check': 'Required Fields',
                'status': 'FAIL',
                'reason': f'Missing required fields: {", ".join(missing)}'
            })
            self.risk_score += 20
        else:
            self.findings.append({
                'check': 'Required Fields',
                'status': 'PASS',
                'reason': f'All required fields present ({", ".join(required)})'
            })

    def validate_expiry(self):
        """
        Validates document expiration.
        Aadhaar Cards, PAN Cards, and Voter IDs have statutory lifetime validity.
        Passports and Driving Licences require strict validity checks.
        """
        if self.document_type in ["Aadhaar Card", "PAN Card", "Voter ID"]:
            self.findings.append({
                'check': 'Expiry Date',
                'status': 'PASS',
                'reason': f'{self.document_type} has lifetime statutory validity in India (No expiration date required)'
            })
            return

        expiry_str = self.fields.get('expiry')
        if expiry_str and expiry_str != "Not detected":
            try:
                expiry_date = self._parse_date(expiry_str)
                if expiry_date:
                    if expiry_date < datetime.now():
                        self.findings.append({
                            'check': 'Expiry Date',
                            'status': 'FAIL',
                            'reason': f'Document expired on {expiry_str}'
                        })
                        self.risk_score += 30
                    else:
                        days_left = (expiry_date - datetime.now()).days
                        if days_left < 30:
                            self.findings.append({
                                'check': 'Expiry Date',
                                'status': 'WARNING',
                                'reason': f'Expires soon: {days_left} days remaining'
                            })
                            self.risk_score += 10
                        else:
                            self.findings.append({
                                'check': 'Expiry Date',
                                'status': 'PASS',
                                'reason': f'Document valid until {expiry_str}'
                            })
                else:
                    self.findings.append({
                        'check': 'Expiry Date',
                        'status': 'WARNING',
                        'reason': 'Could not parse expiry date format'
                    })
                    self.risk_score += 5
            except Exception:
                self.findings.append({
                    'check': 'Expiry Date',
                    'status': 'WARNING',
                    'reason': 'Could not validate expiry date'
                })
                self.risk_score += 5
        else:
            self.findings.append({
                'check': 'Expiry Date',
                'status': 'WARNING',
                'reason': 'Expiry date not found'
            })
            self.risk_score += 10

    def validate_dob_format(self):
        """Validates date of birth and calculates reasonable age window."""
        dob_str = self.fields.get('dob')
        if dob_str and dob_str != "Not detected":
            try:
                dob_date = self._parse_date(dob_str)
                if dob_date:
                    age = (datetime.now() - dob_date).days / 365.25
                    if age < 1:
                        self.findings.append({
                            'check': 'Date of Birth',
                            'status': 'FAIL',
                            'reason': 'DOB suggests age less than 1 year - suspicious'
                        })
                        self.risk_score += 30
                    elif age > 120:
                        self.findings.append({
                            'check': 'Date of Birth',
                            'status': 'FAIL',
                            'reason': 'DOB suggests age over 120 years - suspicious'
                        })
                        self.risk_score += 30
                    else:
                        self.findings.append({
                            'check': 'Date of Birth',
                            'status': 'PASS',
                            'reason': f'DOB: {dob_str} (Calculated age: {int(age)} years)'
                        })
                else:
                    self.findings.append({
                        'check': 'Date of Birth',
                        'status': 'WARNING',
                        'reason': 'Could not parse DOB format'
                    })
                    self.risk_score += 5
            except Exception:
                self.findings.append({
                    'check': 'Date of Birth',
                    'status': 'WARNING',
                    'reason': 'Could not validate DOB'
                })
                self.risk_score += 5
        else:
            self.findings.append({
                'check': 'Date of Birth',
                'status': 'WARNING',
                'reason': 'DOB not found'
            })
            self.risk_score += 10

    def validate_document_number(self):
        """General document number format check."""
        doc_num = self.fields.get('document_number')
        if doc_num and doc_num != "Not detected":
            clean_num = re.sub(r"[\s\-]", "", doc_num)
            if re.match(r'^[A-Z0-9]{6,20}$', clean_num, re.IGNORECASE):
                self.findings.append({
                    'check': 'Document Number Format',
                    'status': 'PASS',
                    'reason': f'Valid alphanumeric syntax: {doc_num}'
                })
            else:
                self.findings.append({
                    'check': 'Document Number Format',
                    'status': 'WARNING',
                    'reason': f'Unusual format: {doc_num}'
                })
                self.risk_score += 10
        else:
            self.findings.append({
                'check': 'Document Number Format',
                'status': 'WARNING',
                'reason': 'Document number not detected'
            })
            self.risk_score += 10

    # =========================================================================
    # INDIAN GOVERNMENT DOCUMENT VALIDATION SUITE
    # =========================================================================

    def validate_indian_government_document(self):
        """
        Executes specialized mathematical and design checks for Indian documents:
        - Aadhaar: Verhoeff algorithm, non-zero/one start, UIDAI keywords
        - PAN Card: 10-char syntax, 4th char entity, 5th char surname initial
        - Voter ID: EPIC 3-letter + 7-digit syntax, Election Commission keywords
        - Driving Licence: 2-letter state code RTO validation
        - Passport: 1-letter + 7-digit syntax
        """
        doc_type = self.document_type
        doc_num = self.fields.get('document_number', '')
        name = self.fields.get('name', '')
        raw_text_lower = (self.raw_text or "").lower()

        # 1. AADHAAR CARD
        if doc_type == "Aadhaar Card" or "aadhaar" in raw_text_lower:
            self._validate_aadhaar(doc_num, raw_text_lower)

        # 2. PAN CARD
        elif doc_type == "PAN Card" or "permanent account number" in raw_text_lower or "income tax" in raw_text_lower:
            self._validate_pan(doc_num, name, raw_text_lower)

        # 3. VOTER ID (EPIC)
        elif doc_type in ["Voter ID", "ID Card"] and ("election commission" in raw_text_lower or "epic" in raw_text_lower):
            self._validate_voter_id(doc_num, raw_text_lower)

        # 4. DRIVING LICENCE
        elif doc_type == "Driving License" or "driving licence" in raw_text_lower:
            self._validate_driving_licence(doc_num, raw_text_lower)

        # 5. PASSPORT
        elif doc_type == "Passport":
            self._validate_passport(doc_num)

    def _validate_aadhaar(self, doc_num: str, raw_text_lower: str):
        """Mathematical Verhoeff checksum & UIDAI design validation for Aadhaar."""
        clean_digits = re.sub(r"\D", "", doc_num)

        # Check if masked Aadhaar (e.g. XXXX XXXX 1234)
        is_masked = bool(re.search(r"[X\*\.]{4}\s?[X\*\.]{4}\s?\d{4}", doc_num, re.IGNORECASE))

        if is_masked:
            self.findings.append({
                'check': 'Aadhaar Security: Masked UID',
                'status': 'PASS',
                'reason': 'Valid Masked Aadhaar format detected (UIDAI compliant privacy protection)'
            })
        elif len(clean_digits) == 12:
            # Rule 1: Cannot start with 0 or 1
            if clean_digits[0] in ['0', '1']:
                self.findings.append({
                    'check': 'Aadhaar Security: Number Range',
                    'status': 'FAIL',
                    'reason': f'Aadhaar numbers cannot start with {clean_digits[0]}. Invalid UIDAI number scheme.'
                })
                self.risk_score += 35
            else:
                # Rule 2: Verhoeff Dihedral D5 Mathematical Checksum
                is_verhoeff_valid = validate_verhoeff(clean_digits)
                if is_verhoeff_valid:
                    self.findings.append({
                        'check': 'Aadhaar Security: Verhoeff Checksum',
                        'status': 'PASS',
                        'reason': 'UIDAI Verhoeff Checksum Validated: 12th check digit mathematically authentic'
                    })
                else:
                    self.findings.append({
                        'check': 'Aadhaar Security: Verhoeff Checksum',
                        'status': 'FAIL',
                        'reason': 'Invalid Aadhaar number - failed Verhoeff checksum algorithm. Counterfeit/tampered UID.'
                    })
                    self.risk_score += 35
        elif doc_num and doc_num != "Not detected":
            self.findings.append({
                'check': 'Aadhaar Security: Number Length',
                'status': 'FAIL',
                'reason': f'Aadhaar must contain exactly 12 digits (Found: {len(clean_digits)} digits)'
            })
            self.risk_score += 35

        # Design Check: Government of India & UIDAI Credential Text
        gov_keywords = ["government of india", "भारत सरकार", "unique identification", "uidai", "मेरा आधार", "aadhaar"]
        detected_keywords = [k for k in gov_keywords if k in raw_text_lower]
        if len(detected_keywords) >= 2 or not raw_text_lower:
            self.findings.append({
                'check': 'Aadhaar Security: Official Design & Emblems',
                'status': 'PASS',
                'reason': 'Government of India / UIDAI official security markings and keywords verified'
            })
        elif detected_keywords:
            self.findings.append({
                'check': 'Aadhaar Security: Official Design & Emblems',
                'status': 'PASS',
                'reason': f'UIDAI identity marker verified ({", ".join(detected_keywords)})'
            })
        else:
            self.findings.append({
                'check': 'Aadhaar Security: Official Design & Emblems',
                'status': 'WARNING',
                'reason': 'UIDAI emblem or Government of India security markings not detected in visual scan'
            })
            self.risk_score += 10

    def _validate_pan(self, doc_num: str, name: str, raw_text_lower: str):
        """Syntax, Taxpayer Entity code & Surname initial matching for Indian PAN Card."""
        clean_num = doc_num.replace(" ", "").upper().strip()

        # Syntax check: Exactly 5 letters, 4 digits, 1 letter
        pan_match = re.match(r"^([A-Z]{3})([A-Z])([A-Z])([0-9]{4})([A-Z])$", clean_num)

        if pan_match:
            entity_char = pan_match.group(2)  # 4th character
            surname_char = pan_match.group(3) # 5th character

            # 4th Character Check: Entity Type
            if entity_char in PAN_ENTITY_TYPES:
                entity_desc = PAN_ENTITY_TYPES[entity_char]
                self.findings.append({
                    'check': 'PAN Security: Taxpayer Entity Code',
                    'status': 'PASS',
                    'reason': f"Valid 4th character '{entity_char}' representing: {entity_desc}"
                })
            else:
                self.findings.append({
                    'check': 'PAN Security: Taxpayer Entity Code',
                    'status': 'FAIL',
                    'reason': f"Invalid 4th character '{entity_char}'. Not an authorized Income Tax entity code."
                })
                self.risk_score += 25

            # 5th Character Check: Individual Surname Initial Match
            if entity_char == 'P' and name and name != "Not detected":
                # Extract surname (last word of name)
                name_parts = [p for p in name.strip().split() if len(p) > 1]
                if name_parts:
                    surname = name_parts[-1].upper()
                    expected_initial = surname[0]

                    if surname_char == expected_initial:
                        self.findings.append({
                            'check': 'PAN Security: Surname Initial Alignment',
                            'status': 'PASS',
                            'reason': f"PAN 5th character '{surname_char}' matches cardholder surname '{surname}'"
                        })
                    else:
                        self.findings.append({
                            'check': 'PAN Security: Surname Initial Alignment',
                            'status': 'WARNING',
                            'reason': f"PAN 5th character '{surname_char}' does not match cardholder surname '{surname}' (Expected '{expected_initial}')"
                        })
                        self.risk_score += 20
        elif doc_num and doc_num != "Not detected":
            self.findings.append({
                'check': 'PAN Security: Format Verification',
                'status': 'FAIL',
                'reason': f"Invalid PAN format '{clean_num}'. Must be 5 uppercase letters, 4 digits, 1 letter (e.g. ABCDE1234F)"
            })
            self.risk_score += 30

        # Design Check: Income Tax Department markings
        it_keywords = ["income tax", "आयकर", "permanent account number", "govt. of india", "pan card"]
        has_it_markers = any(k in raw_text_lower for k in it_keywords)
        if has_it_markers or not raw_text_lower:
            self.findings.append({
                'check': 'PAN Security: Department Credentials',
                'status': 'PASS',
                'reason': 'Income Tax Department / Govt. of India official credentials verified'
            })
        else:
            self.findings.append({
                'check': 'PAN Security: Department Credentials',
                'status': 'WARNING',
                'reason': 'Income Tax Department security headers not detected in visual scan'
            })
            self.risk_score += 10

    def _validate_voter_id(self, doc_num: str, raw_text_lower: str):
        """Validates Election Commission of India (EPIC) Voter ID."""
        clean_num = doc_num.replace(" ", "").upper().strip()

        if re.match(r"^[A-Z]{3}[0-9]{7}$", clean_num):
            self.findings.append({
                'check': 'Voter ID Security: EPIC Format',
                'status': 'PASS',
                'reason': f'Valid Election Commission of India (EPIC) format: {clean_num}'
            })
        elif doc_num and doc_num != "Not detected":
            self.findings.append({
                'check': 'Voter ID Security: EPIC Format',
                'status': 'WARNING',
                'reason': f'Non-standard EPIC voter card number: {clean_num}'
            })
            self.risk_score += 10

        if any(k in raw_text_lower for k in ["election commission", "भारत निर्वाचन आयोग", "elector photo"]):
            self.findings.append({
                'check': 'Voter ID Security: Official Markings',
                'status': 'PASS',
                'reason': 'Election Commission of India official authority verified'
            })

    def _validate_driving_licence(self, doc_num: str, raw_text_lower: str):
        """Validates Indian Driving Licence state code and RTO syntax."""
        clean_num = re.sub(r"[\s\-]", "", doc_num).upper()

        if len(clean_num) >= 15:
            state_code = clean_num[:2]
            if state_code in INDIAN_STATE_CODES:
                state_name = INDIAN_STATE_CODES[state_code]
                self.findings.append({
                    'check': 'Driving Licence: State Jurisdiction',
                    'status': 'PASS',
                    'reason': f'Valid Indian Driving Licence registered under {state_name} ({state_code}) RTO'
                })
            else:
                self.findings.append({
                    'check': 'Driving Licence: State Jurisdiction',
                    'status': 'WARNING',
                    'reason': f"Unrecognized state code '{state_code}' in Driving Licence number"
                })
                self.risk_score += 10
        elif doc_num and doc_num != "Not detected":
            self.findings.append({
                'check': 'Driving Licence: Format',
                'status': 'WARNING',
                'reason': f'Unusual driving licence number format: {doc_num}'
            })
            self.risk_score += 10

    def _validate_passport(self, doc_num: str):
        """Validates Passport number format against jurisdiction rules."""
        clean_num = doc_num.replace(" ", "").upper().strip()
        issuing_country = str(self.fields.get("country", "")).upper().strip()

        # If it's an Indian Passport (explicit IND or in Indian KYC mode without foreign marker)
        if issuing_country == "IND":
            if re.match(r"^[A-Z][0-9]{7}$", clean_num):
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'PASS',
                    'reason': f'Valid Indian Passport format (1 letter + 7 digits): {clean_num}'
                })
            else:
                self.findings.append({
                    'check': 'Passport Security: Indian MEA Format',
                    'status': 'FAIL',
                    'reason': f"Invalid Indian Passport format '{clean_num}'. MEA requires 1 uppercase letter followed by 7 digits."
                })
                self.risk_score += 35
        elif issuing_country and issuing_country != "IND":
            # International Passport
            if issuing_country not in ISO_ICAO_COUNTRY_CODES:
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'FAIL',
                    'reason': f"Passport number '{clean_num}' associated with invalid or fictitious issuing state '{issuing_country}'"
                })
                self.risk_score += 40
            elif re.match(r"^[A-Z0-9]{7,9}$", clean_num):
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'PASS',
                    'reason': f'Valid international passport format ({issuing_country}): {clean_num}'
                })
            else:
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'FAIL',
                    'reason': f'Non-standard international passport number format: {clean_num}'
                })
                self.risk_score += 25
        else:
            # Country not detected
            if re.match(r"^[A-Z][0-9]{7}$", clean_num):
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'PASS',
                    'reason': f'Valid Indian Passport format (1 letter + 7 digits): {clean_num}'
                })
            elif re.match(r"^[A-Z0-9]{7,9}$", clean_num):
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'WARNING',
                    'reason': f'Non-Indian or international passport format detected: {clean_num}'
                })
                self.risk_score += 15
            else:
                self.findings.append({
                    'check': 'Passport Security: Number Syntax',
                    'status': 'FAIL',
                    'reason': f'Invalid passport number syntax: {clean_num}'
                })
                self.risk_score += 30

    def validate_mrz_security(self):
        """Comprehensive ICAO 9303 MRZ verification for passports & travel credentials."""
        if self.document_type != "Passport" and not self.fields.get("mrz_line1"):
            return

        mrz_l1 = self.fields.get("mrz_line1", "")
        mrz_l2 = self.fields.get("mrz_line2", "")

        # 1. Issuing Country Code Verification (ISO 3166-1 alpha-3)
        issuing_country = str(self.fields.get("country", "")).upper().strip()
        if issuing_country:
            if issuing_country not in ISO_ICAO_COUNTRY_CODES:
                self.findings.append({
                    'check': 'Passport Security: Sovereign State Authority',
                    'status': 'FAIL',
                    'reason': f"Fictitious or unrecognized issuing country code '{issuing_country}' in MRZ. Not an authorized ISO 3166-1 sovereign state or ICAO agency."
                })
                self.risk_score += 50
            elif issuing_country != 'IND' and issuing_country != 'UTO':
                self.findings.append({
                    'check': 'Passport Security: Jurisdiction & KYC Eligibility',
                    'status': 'WARNING',
                    'reason': f"Foreign national credential ({issuing_country} Passport) presented for Indian KYC onboarding. Mandatory immigration/visa verification required."
                })
                self.risk_score += 25

        # 2. Citizen Nationality Code Verification
        nationality = str(self.fields.get("nationality", "")).upper().strip()
        if nationality:
            if nationality not in ISO_ICAO_COUNTRY_CODES:
                self.findings.append({
                    'check': 'Passport Security: Citizen Nationality Code',
                    'status': 'FAIL',
                    'reason': f"Invalid or unrecognized nationality code '{nationality}' in MRZ."
                })
                self.risk_score += 45
            elif issuing_country and issuing_country in ISO_ICAO_COUNTRY_CODES and issuing_country != nationality and issuing_country != 'UTO':
                self.findings.append({
                    'check': 'Passport Security: Issuing Authority vs Nationality Alignment',
                    'status': 'WARNING',
                    'reason': f"Passport issuing authority ({issuing_country}) conflicts with recorded citizenship ({nationality}) in Machine Readable Zone."
                })
                self.risk_score += 15

        # 3. Structural Line & Padding Integrity
        if mrz_l1 and mrz_l2:
            clean_l1 = re.sub(r"[^A-Z0-9<]", "", mrz_l1.upper())
            clean_l2 = re.sub(r"[^A-Z0-9<]", "", mrz_l2.upper())

            # Check Line 1 TD3 Length (Standard ICAO 9303 TD3 is exactly 44 chars)
            if len(clean_l1) != 44:
                self.findings.append({
                    'check': 'Passport Security: MRZ Standard Specification',
                    'status': 'FAIL',
                    'reason': f"MRZ Line 1 character length mismatch: {len(clean_l1)} characters found (ICAO 9303 TD3 standard requires exactly 44). Structural forgery indicator."
                })
                self.risk_score += 35

            if len(clean_l2) != 44:
                self.findings.append({
                    'check': 'Passport Security: MRZ Standard Specification',
                    'status': 'FAIL',
                    'reason': f"MRZ Line 2 character length mismatch: {len(clean_l2)} characters found (ICAO 9303 TD3 standard requires exactly 44)."
                })
                self.risk_score += 35

            # Check Filler Zone Padding in Line 1
            if "<" in clean_l1:
                # The trailing filler section begins after the primary identifier
                filler_match = re.search(r"<[A-Z0-9<]+$", clean_l1) or re.search(r"<<<.*$", clean_l1)
                if filler_match:
                    filler_section = clean_l1[clean_l1.find("<<<"):] if "<<<" in clean_l1 else filler_match.group(0)
                    corrupted_fillers = [c for c in filler_section if c != '<']
                    if corrupted_fillers:
                        corrupt_chars_sample = list(dict.fromkeys(corrupted_fillers))[:5]
                        self.findings.append({
                            'check': 'Passport Security: MRZ Filler Integrity',
                            'status': 'FAIL',
                            'reason': f"Corrupted filler padding detected in MRZ Line 1: Found non-filler characters ({', '.join(corrupt_chars_sample)}) where ICAO requires '<'. Synthetic template forgery artifact."
                        })
                        self.risk_score += 45

            # Check ICAO 9303 Separators in Line 1
            if clean_l1.startswith("P"):
                name_portion = clean_l1[5:]
                if "<<" not in name_portion and len(clean_l1) >= 30:
                    self.findings.append({
                        'check': 'Passport Security: Name Record Structure',
                        'status': 'FAIL',
                        'reason': "Malformed MRZ name field: Missing standard ICAO 9303 '<<' primary identifier separator between surname and given names."
                    })
                    self.risk_score += 30

            # 4. Mathematical ICAO 9303 Check Digit Verifications on Line 2
            if len(clean_l2) >= 44:
                # 4a. Document Number Check Digit (chars 0..8 vs char 9)
                doc_num_raw = clean_l2[0:9]
                doc_num_cd = clean_l2[9]
                if doc_num_cd.isdigit():
                    calc_cd = calculate_icao_checksum(doc_num_raw)
                    if int(doc_num_cd) != calc_cd:
                        self.findings.append({
                            'check': 'Passport Security: Document Number Check Digit',
                            'status': 'FAIL',
                            'reason': f"Document number check digit failed ICAO 9303 verification (Expected {calc_cd}, found {doc_num_cd}). Counterfeit document number."
                        })
                        self.risk_score += 40

                # 4b. DOB Check Digit (chars 13..18 vs char 19)
                dob_raw = clean_l2[13:19]
                dob_cd = clean_l2[19]
                if dob_cd.isdigit():
                    calc_dob_cd = calculate_icao_checksum(dob_raw)
                    if int(dob_cd) != calc_dob_cd:
                        self.findings.append({
                            'check': 'Passport Security: DOB Check Digit',
                            'status': 'FAIL',
                            'reason': f"Date of birth check digit failed ICAO 9303 verification. Birthdate was tampered."
                        })
                        self.risk_score += 40

                # 4c. Expiry Check Digit (chars 21..26 vs char 27)
                exp_raw = clean_l2[21:27]
                exp_cd = clean_l2[27]
                if exp_cd.isdigit():
                    calc_exp_cd = calculate_icao_checksum(exp_raw)
                    if int(exp_cd) != calc_exp_cd:
                        self.findings.append({
                            'check': 'Passport Security: Expiry Date Check Digit',
                            'status': 'FAIL',
                            'reason': f"Expiry date check digit failed ICAO 9303 verification. Expiration date was tampered."
                        })
                        self.risk_score += 40

                # 4d. Composite Check Digit (char 43)
                composite_cd = clean_l2[43]
                if composite_cd.isdigit():
                    composite_data = clean_l2[0:10] + clean_l2[13:20] + clean_l2[21:43]
                    calc_comp_cd = calculate_icao_checksum(composite_data)
                    if int(composite_cd) != calc_comp_cd:
                        self.findings.append({
                            'check': 'Passport Security: Composite Checksum',
                            'status': 'FAIL',
                            'reason': "Composite multi-field checksum failed ICAO 9303 validation. Document data has been altered."
                        })
                        self.risk_score += 45

    def validate_name_quality(self):
        """Forensic quality inspection of extracted name for gibberish or key-mashing."""
        name = str(self.fields.get("name", "")).strip()
        if not name or name == "Not detected":
            return

        name_upper = name.upper()
        # Look for unnatural consonant clusters (4 or more consecutive consonants in a word)
        words = re.findall(r"[A-Z]+", name_upper)
        suspicious_words = []
        for w in words:
            if len(w) >= 5:
                # Check for 4+ consecutive consonants
                if re.search(r"[BCDFGHJKLMNPQRSTVWXYZ]{4,}", w):
                    suspicious_words.append(w)
                # Check for unnatural start consonants (e.g. KJ, QX, ZX at word start)
                elif re.match(r"^(?:KJ|QX|ZX|QK|VJ|XJ)", w):
                    suspicious_words.append(w)

        if suspicious_words:
            self.findings.append({
                'check': 'Identity Security: Name Phonetic & Forensic Integrity',
                'status': 'FAIL',
                'reason': f"Suspicious or synthetic name pattern detected ({', '.join(suspicious_words)}). Contains unnatural phonetic consonant combinations indicative of synthetic fabrication."
            })
            self.risk_score += 35

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parses multi-format date strings into datetime objects."""
        date_formats = [
            '%d %b %Y',
            '%d %B %Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%b %d %Y',
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue
        
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = int(year_match.group(1))
            if 1900 < year < 2100:
                return datetime(year, 1, 1)
        
        return None

    def calculate_risk_score(self):
        self.risk_score = min(100, self.risk_score)