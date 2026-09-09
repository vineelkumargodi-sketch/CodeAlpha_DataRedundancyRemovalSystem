from datetime import datetime, timezone

from app import db


class ValidationLog(db.Model):
    __tablename__ = "validation_logs"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(150),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False
    )

    message = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )