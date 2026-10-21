"""
User, Role, Permission, Customer, and Agent Models.
Implements Role-Based Access Control (ADMIN, AGENT, CUSTOMER).
"""

from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.models.types import BigIntPK
from app.utils.security import hash_password, verify_password


role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # ADMIN, AGENT, CUSTOMER
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    users = db.relationship("User", back_populates="role", lazy="dynamic")
    permissions = db.relationship("Permission", secondary=role_permissions, backref="roles", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": [p.name for p in self.permissions],
        }


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    role = db.relationship("Role", back_populates="users", lazy="joined")
    customer_profile = db.relationship("Customer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    agent_profile = db.relationship("Agent", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", lazy="dynamic")
    transactions = db.relationship("Transaction", back_populates="user", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def has_role(self, role_name: str) -> bool:
        return self.role is not None and self.role.name.upper() == role_name.upper()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role.name if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "customer_profile": self.customer_profile.to_dict() if self.customer_profile else None,
            "agent_profile": self.agent_profile.to_dict() if self.agent_profile else None,
        }


class Customer(db.Model):
    __tablename__ = "customers"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    momo_number = db.Column(db.String(20), nullable=True)
    momo_network = db.Column(db.String(20), nullable=True)  # MTN, TELECEL, AT
    wallet_balance = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="customer_profile")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "momo_number": self.momo_number,
            "momo_network": self.momo_network,
            "wallet_balance": float(self.wallet_balance),
        }


class Agent(db.Model):
    __tablename__ = "agents"
    __table_args__ = {"sqlite_autoincrement": True}

    id = BigIntPK()
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    agent_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    business_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    commission_balance = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    wallet_balance = db.Column(db.Numeric(12, 4), default=Decimal("0.0000"), nullable=False)
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED, PENDING
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="agent_profile")
    orders = db.relationship("Order", back_populates="agent", lazy="dynamic")
    commissions = db.relationship("Commission", back_populates="agent", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "agent_code": self.agent_code,
            "business_name": self.business_name,
            "location": self.location,
            "commission_balance": float(self.commission_balance),
            "wallet_balance": float(self.wallet_balance),
            "status": self.status,
        }
