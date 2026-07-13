from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, String, Column, String, func, ForeignKey, Enum as SqlEnum
from enum import Enum
from datetime import date, datetime
from typing import Optional
from sqlalchemy.sql.sqltypes import DateTime


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="userrole"), default=UserRole.USER, nullable=False
    )


class Contacts(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user_id: Mapped[int | None] = mapped_column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user: Mapped["User"] = relationship("User", backref="contacts")
