"""
Audit Logging, Notification Queue, and System Integration Settings Models.
"""

from datetime import datetime, timezone
from app.extensions import db
from app.models.types import BigIntPK


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "SYSTEM",
            "action": self.action,
            "ip_address": self.ip_address,
            "details": self.details_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Notification(db.Model):
    __tablename__ = "notifications"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    recipient = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), default="SMS", nullable=False)  # SMS, PUSH, EMAIL
    template = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="PENDING", nullable=False)  # PENDING, SENT, FAILED
    provider_response = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "recipient": self.recipient,
            "channel": self.channel,
            "template": self.template,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class IntegrationSetting(db.Model):
    __tablename__ = "integration_settings"

    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(50), unique=True, nullable=False)  # MTN_MOMO, HUBTEL, PAYSTACK, AIRTIME_AGGREGATOR
    is_enabled = db.Column(db.Boolean, default=False, nullable=False)
    is_sandbox = db.Column(db.Boolean, default=True, nullable=False)
    config_json = db.Column(db.JSON, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "provider_name": self.provider_name,
            "is_enabled": self.is_enabled,
            "is_sandbox": self.is_sandbox,
            "config": self.config_json,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
