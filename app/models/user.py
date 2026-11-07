"""SQLAlchemy User model with unique username/email and a hashed password."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.security import hash_password, verify_password

if TYPE_CHECKING:  # pragma: no cover
    from app.models.calculation import Calculation


def utc_now() -> datetime:
    """Current time in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class User(Base):
    """A registered user. Only the password hash is stored, never the plain password."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    calculations: Mapped[list["Calculation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def set_password(self, plain_password: str) -> None:
        """Hash the plain password and store it in password_hash."""
        self.password_hash = hash_password(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """Return True if plain_password matches this user's stored hash."""
        return verify_password(plain_password, self.password_hash)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"