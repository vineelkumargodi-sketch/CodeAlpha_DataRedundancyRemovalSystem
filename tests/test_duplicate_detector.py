from app.services.duplicate_detector import (
    normalize_text,
    normalize_phone,
    create_fingerprint,
    prepare_record,
    calculate_name_similarity,
    classify_possible_duplicate,
)
from app.services.validation import validate_record


class FakeRecord:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone


def test_text_normalization():
    assert normalize_text(
        "  John   Smith  "
    ) == "john smith"


def test_phone_normalization():
    assert normalize_phone(
        "+91 98765-43210"
    ) == "919876543210"


def test_same_data_has_same_fingerprint():
    fingerprint_1 = create_fingerprint(
        "John Smith",
        "JOHN@example.com",
        "+91 98765 43210"
    )

    fingerprint_2 = create_fingerprint(
        " john   smith ",
        "john@example.com",
        "919876543210"
    )

    assert fingerprint_1 == fingerprint_2


def test_prepare_record():
    result = prepare_record(
        "John Smith",
        "john@example.com",
        "+91 98765 43210"
    )

    assert result["normalized_name"] == "john smith"
    assert result["normalized_email"] == "john@example.com"
    assert result["normalized_phone"] == "919876543210"
    assert len(result["fingerprint"]) == 64


def test_validation():
    assert validate_record(
        "John Smith",
        "john@example.com",
        "9876543210"
    ) == (
        True,
        "Valid record."
    )


def test_invalid_email():
    valid, message = validate_record(
        "John Smith",
        "not-an-email"
    )

    assert valid is False
    assert message == "Invalid email format."


def test_name_similarity():
    similarity = calculate_name_similarity(
        "John Smith",
        "John Smit"
    )

    assert similarity >= 0.70


def test_possible_duplicate_by_email():
    existing = FakeRecord(
        "John Smith",
        "john@example.com",
        "+91 98765 43210"
    )

    result = classify_possible_duplicate(
        "John Smit",
        "john@example.com",
        "+91 11111 11111",
        existing
    )

    assert result["status"] == "POSSIBLE_DUPLICATE"
    assert result["email_match"] is True


def test_unique_when_identity_does_not_match():
    existing = FakeRecord(
        "John Smith",
        "john@example.com",
        "+91 98765 43210"
    )

    result = classify_possible_duplicate(
        "Ravi Kumar",
        "ravi@example.com",
        "+91 91234 56789",
        existing
    )

    assert result["status"] == "UNIQUE"