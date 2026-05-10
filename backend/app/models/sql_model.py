from app import db
from datetime import datetime, timezone


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, default="")
    result = db.Column(db.Float)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "code": self.code,
            "value": self.value,
            "description": self.description,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
