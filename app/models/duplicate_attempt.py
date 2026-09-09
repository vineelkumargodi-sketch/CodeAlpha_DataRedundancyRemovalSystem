from datetime import datetime, timezone

from app import db


class DuplicateAttempt(db.Model):
    __tablename__ = "duplicate_attempts"

    id = db.Column(db.Integer, primary_key=True)

    submitted_name = db.Column(
        db.String(150),
        nullable=False
    )

    submitted_email = db.Column(
        db.String(150),
        nullable=False
    )

    submitted_phone = db.Column(
        db.String(30),
        nullable=True
    )

    reason = db.Column(
        db.String(255),
        nullable=False
    )

    matched_record_id = db.Column(
        db.Integer,
        db.ForeignKey("records.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )