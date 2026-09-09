from datetime import datetime, timezone

from app import db


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=True)

    normalized_name = db.Column(db.String(150), nullable=False)
    normalized_email = db.Column(db.String(150), nullable=False)
    normalized_phone = db.Column(db.String(30), nullable=False)

    fingerprint = db.Column(
        db.String(64),
        nullable=False,
        unique=True,
        index=True
    )

    verified = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "verified": self.verified,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }