import re


PHONE_FORMAT_ERROR = "Phone number must be in +998######### format."


def normalize_uz_phone(value):
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("Phone number is required.")

    digits = re.sub(r"\D", "", raw)

    if digits.startswith("998") and len(digits) == 12:
        national_part = digits[3:]
    elif digits.startswith("0") and len(digits) == 10:
        national_part = digits[1:]
    elif len(digits) == 9:
        national_part = digits
    else:
        raise ValueError(PHONE_FORMAT_ERROR)

    if len(national_part) != 9 or not national_part.isdigit():
        raise ValueError(PHONE_FORMAT_ERROR)

    return f"+998{national_part}"
