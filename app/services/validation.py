import re


def validate_record(name, email, phone=None):
    """
    Validate incoming record data.

    Returns:
        (True, "Valid record")
        or
        (False, "Validation error message")
    """

    if not name or not name.strip():
        return False, "Name is required."

    if not email or not email.strip():
        return False, "Email is required."

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(email_pattern, email.strip()):
        return False, "Invalid email format."

    if phone:
        digits = re.sub(r"\D", "", phone)

        if len(digits) < 10:
            return False, "Phone number must contain at least 10 digits."

    return True, "Valid record."