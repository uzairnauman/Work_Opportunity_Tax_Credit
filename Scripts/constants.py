# Scripts/constants.py

POSITIONS = ["LPN", "RN", "CNA", "CHHA", "ADMIN", "CG"]

RATINGS = [
    "0 - Not Applicable",
    "1 - Unacceptable",
    "3 - Meets Expectations",
    "4 - Exceeds Expectations"
]

EDUCATION = [
    "High School",
    "Associate Degree",
    "4 year College"
]

LANGUAGES = [
    "English",
    "English, Spanish",
    "English, French"
]

TERMINATION_STATUSES = [
    "Resigned/Separated - Eligible for Rehire",
    "Resigned/Separated - Not Eligible for Rehire"
]

# --- Shift / Client system (new system effective 07/01/2026) ---

PAYER_TYPES = [
    "Private Pay",
    "Medicaid",
    "Medicare",
    "LTC Insurance",
    "VA Benefits"
]

CARE_TYPES = [
    "Personal Care",
    "Companion Care",
    "Skilled Nursing",
    "Respite Care",
    "Homemaker Services"
]

CLIENT_STATUSES = [
    "Active",
    "Active - On Hold",
    "Discharged - Completed",
    "Discharged - Hospitalized",
    "Discharged - Deceased",
    "Discharged - Family Request"
]

# Position required by a client maps loosely onto employee POSITIONS
CLIENT_REQUIRED_POSITIONS = ["CNA", "CHHA", "LPN", "RN", "CG"]

SHIFT_STATUSES = [
    "Completed",
    "Cancelled - Client",
    "Cancelled - Employee",
    "No-Show",
    "Scheduled"
]

# weights line up positionally with SHIFT_STATUSES above
SHIFT_STATUS_WEIGHTS = [0.82, 0.06, 0.05, 0.04, 0.03]

SHIFT_START_TIMES = ["06:00", "07:00", "08:00", "09:00", "14:00", "15:00", "22:00"]
SHIFT_LENGTH_HOURS_OPTIONS = [4, 6, 8, 12]
