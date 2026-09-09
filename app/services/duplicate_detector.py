import hashlib
import re
from difflib import SequenceMatcher


def normalize_text(value):
    """Normalize general text for consistent comparison."""

    if value is None:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_email(email):
    """Normalize an email address."""

    return normalize_text(email)


def normalize_phone(phone):
    """Keep only digits from a phone number."""

    if not phone:
        return ""

    return re.sub(r"\D", "", str(phone))


def create_fingerprint(name, email, phone):
    """Create a SHA-256 fingerprint from normalized values."""

    normalized_name = normalize_text(name)
    normalized_email = normalize_email(email)
    normalized_phone = normalize_phone(phone)

    raw_data = (
        f"{normalized_name}|"
        f"{normalized_email}|"
        f"{normalized_phone}"
    )

    return hashlib.sha256(
        raw_data.encode("utf-8")
    ).hexdigest()


def prepare_record(name, email, phone=None):
    """Normalize incoming data and generate its fingerprint."""

    normalized_name = normalize_text(name)
    normalized_email = normalize_email(email)
    normalized_phone = normalize_phone(phone)

    return {
        "normalized_name": normalized_name,
        "normalized_email": normalized_email,
        "normalized_phone": normalized_phone,
        "fingerprint": create_fingerprint(
            name,
            email,
            phone
        ),
    }


def calculate_name_similarity(name1, name2):
    """
    Return a similarity score between 0.0 and 1.0.
    1.0 means the names are identical after normalization.
    """

    first = normalize_text(name1)
    second = normalize_text(name2)

    if not first or not second:
        return 0.0

    return SequenceMatcher(
        None,
        first,
        second
    ).ratio()


def classify_possible_duplicate(
    incoming_name,
    incoming_email,
    incoming_phone,
    existing_record
):
    """
    Classify a record as a possible duplicate when:
    - email matches exactly and name is reasonably similar, OR
    - phone matches exactly and name is reasonably similar.
    """

    incoming_email = normalize_email(incoming_email)
    incoming_phone = normalize_phone(incoming_phone)

    existing_email = normalize_email(
        existing_record.email
    )

    existing_phone = normalize_phone(
        existing_record.phone
    )

    name_similarity = calculate_name_similarity(
        incoming_name,
        existing_record.name
    )

    email_match = (
        bool(incoming_email)
        and incoming_email == existing_email
    )

    phone_match = (
        bool(incoming_phone)
        and incoming_phone == existing_phone
    )

    strong_identity_match = (
        email_match or phone_match
    )

    if strong_identity_match and name_similarity >= 0.70:
        return {
            "status": "POSSIBLE_DUPLICATE",
            "name_similarity": round(
                name_similarity,
                3
            ),
            "email_match": email_match,
            "phone_match": phone_match,
        }

    return {
        "status": "UNIQUE",
        "name_similarity": round(
            name_similarity,
            3
        ),
        "email_match": email_match,
        "phone_match": phone_match,
    }