"""Database operations for users and calculations."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationCreate
from app.schemas.user import UserCreate


class DuplicateUserError(Exception):
    """Raised when the username or email is already registered."""


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a user, storing only a hash of the password."""
    user = User(username=user_in.username, email=user_in.email)
    user.set_password(user_in.password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateUserError("Username or email already exists") from exc
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    """Return the user with this id, or None."""
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    """Return the user with this username, or None."""
    return db.scalars(select(User).where(User.username == username)).first()


def create_calculation(db: Session, calc_in: CalculationCreate, user_id: int) -> Calculation:
    """Compute the result with the factory and store the calculation for a user."""
    calculation = Calculation(a=calc_in.a, b=calc_in.b, type=calc_in.type.value, user_id=user_id)
    calculation.result = calculation.compute_result()
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


def get_calculation(db: Session, calculation_id: int) -> Calculation | None:
    """Return the calculation with this id, or None."""
    return db.get(Calculation, calculation_id)


def list_calculations_for_user(db: Session, user_id: int) -> list[Calculation]:
    """Return all calculations that belong to a user, oldest first."""
    stmt = select(Calculation).where(Calculation.user_id == user_id).order_by(Calculation.id)
    return list(db.scalars(stmt))