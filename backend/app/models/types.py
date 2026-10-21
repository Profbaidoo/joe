"""
Custom Cross-Database Column Types and Helper Definitions.
Ensures seamless compatibility between MySQL 8.0 (BIGINT AUTO_INCREMENT)
and SQLite (INTEGER PRIMARY KEY AUTOINCREMENT) for local unit testing.
"""

from app.extensions import db


def BigIntPK():
    """Generates a cross-database compatible 64-bit auto-incrementing primary key."""
    return db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )


SQLITE_TABLE_ARGS = {"sqlite_autoincrement": True}
