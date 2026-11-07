"""SQLAlchemy Calculation model linked to a User by a foreign key."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.calculation_factory import CalculationFactory, CalculationType
from app.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User

ALLOWED_TYPES = ", ".join(f"'{t.value}'" for t in CalculationType)


def utc_now() -> datetime:
    """Current time in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class Calculation(Base):
    """One calculation: two operands, a type, the stored result, and its owner."""

    __tablename__ = "calculations"
    __table_args__ = (
        # The database itself rejects unknown types and division by zero
        CheckConstraint(f"type IN ({ALLOWED_TYPES})", name="ck_calculations_type"),
        CheckConstraint("NOT (type = 'Divide' AND b = 0)", name="ck_calculations_no_zero_divisor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    a: Mapped[float] = mapped_column(Float, nullable=False)
    b: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="calculations")

    def compute_result(self) -> float:
        """Compute the result with the factory (does not save it)."""
        return CalculationFactory.create(self.type).compute(self.a, self.b)

    def __repr__(self) -> str:
        return f"<Calculation id={self.id} {self.type}({self.a}, {self.b}) = {self.result}>"