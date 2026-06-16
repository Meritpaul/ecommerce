import re


def normalize_bd_phone(raw_phone):
    """
    Normalizes a Bangladeshi phone number to the standard local 11-digit
    format (01XXXXXXXXX), accepting various input formats:

        +8801812345678   -> 01812345678
        8801812345678    -> 01812345678
        01812345678      -> 01812345678
        +880 1812-345678 -> 01812345678   (spaces/dashes stripped)

    Returns the normalized 11-digit string if valid, otherwise None.
    """
    if not raw_phone:
        return None

    # Strip everything except digits and a leading +
    cleaned = re.sub(r'[^\d+]', '', raw_phone.strip())

    # Remove country code variants
    if cleaned.startswith('+880'):
        cleaned = cleaned[4:]
    elif cleaned.startswith('880') and len(cleaned) > 11:
        cleaned = cleaned[3:]
    elif cleaned.startswith('+'):
        # Unknown country code with a +, not a valid BD number
        return None

    # After stripping country code, we should have exactly 11 digits
    # starting with 01 and a valid operator prefix (3-9)
    if re.fullmatch(r'01[3-9]\d{8}', cleaned):
        return cleaned

    return None


def is_valid_bd_phone(raw_phone):
    """Convenience boolean wrapper around normalize_bd_phone."""
    return normalize_bd_phone(raw_phone) is not None