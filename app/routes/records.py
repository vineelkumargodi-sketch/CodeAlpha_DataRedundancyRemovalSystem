from flask import Blueprint, jsonify, request

from app import db
from app.models import (
    Record,
    DuplicateAttempt,
    ValidationLog
)
from app.services.duplicate_detector import (
    prepare_record,
    classify_possible_duplicate
)
from app.services.validation import validate_record


records_bp = Blueprint("records", __name__)


@records_bp.post("/records")
def create_record():

    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    email = payload.get("email")
    phone = payload.get("phone")

    # ---------------------------------------------------------
    # 1. Validate incoming data
    # ---------------------------------------------------------

    valid, message = validate_record(
        name,
        email,
        phone
    )

    if not valid:

        db.session.add(
            ValidationLog(
                email=email,
                status="INVALID",
                message=message
            )
        )

        db.session.commit()

        return jsonify({
            "status": "INVALID",
            "message": message
        }), 400

    # ---------------------------------------------------------
    # 2. Normalize data and create fingerprint
    # ---------------------------------------------------------

    prepared = prepare_record(
        name,
        email,
        phone
    )

    # ---------------------------------------------------------
    # 3. Check exact duplicate
    # ---------------------------------------------------------

    existing = Record.query.filter_by(
        fingerprint=prepared["fingerprint"]
    ).first()

    if existing:

        db.session.add(
            DuplicateAttempt(
                submitted_name=name,
                submitted_email=email,
                submitted_phone=phone,
                reason="Exact duplicate fingerprint detected",
                matched_record_id=existing.id
            )
        )

        db.session.commit()

        return jsonify({
            "status": "REDUNDANT",
            "message": "Duplicate record rejected.",
            "matched_record_id": existing.id,
            "record": existing.to_dict()
        }), 409

    # ---------------------------------------------------------
    # 4. Check for possible duplicate
    # ---------------------------------------------------------

    existing_records = Record.query.all()

    for existing_record in existing_records:

        classification = classify_possible_duplicate(
            incoming_name=name,
            incoming_email=email,
            incoming_phone=phone,
            existing_record=existing_record
        )

        if classification["status"] == "POSSIBLE_DUPLICATE":

            db.session.add(
                DuplicateAttempt(
                    submitted_name=name,
                    submitted_email=email,
                    submitted_phone=phone,
                    reason=(
                        "Possible duplicate detected: "
                        f"name similarity="
                        f"{classification['name_similarity']}, "
                        f"email_match="
                        f"{classification['email_match']}, "
                        f"phone_match="
                        f"{classification['phone_match']}"
                    ),
                    matched_record_id=existing_record.id
                )
            )

            db.session.commit()

            return jsonify({
                "status": "POSSIBLE_DUPLICATE",
                "message": (
                    "A possible duplicate was detected. "
                    "The record was not stored automatically."
                ),
                "matched_record_id": existing_record.id,
                "name_similarity": classification[
                    "name_similarity"
                ],
                "email_match": classification[
                    "email_match"
                ],
                "phone_match": classification[
                    "phone_match"
                ],
                "record": existing_record.to_dict()
            }), 409

    # ---------------------------------------------------------
    # 5. Store unique verified record
    # ---------------------------------------------------------

    record = Record(
        name=name.strip(),
        email=email.strip(),
        phone=phone.strip()
        if isinstance(phone, str)
        else phone,

        normalized_name=prepared["normalized_name"],
        normalized_email=prepared["normalized_email"],
        normalized_phone=prepared["normalized_phone"],

        fingerprint=prepared["fingerprint"],
        verified=True
    )

    db.session.add(record)

    db.session.add(
        ValidationLog(
            email=email,
            status="VERIFIED",
            message="Unique and verified record accepted."
        )
    )

    db.session.commit()

    return jsonify({
        "status": "UNIQUE",
        "message": "Unique and verified record stored.",
        "record": record.to_dict()
    }), 201


@records_bp.get("/records")
def list_records():

    records = Record.query.order_by(
        Record.id.desc()
    ).all()

    return jsonify({
        "count": len(records),
        "records": [
            record.to_dict()
            for record in records
        ]
    })


@records_bp.get("/stats")
def stats():

    return jsonify({
        "unique_records": Record.query.count(),
        "duplicate_attempts": DuplicateAttempt.query.count(),
        "validation_events": ValidationLog.query.count()
    })