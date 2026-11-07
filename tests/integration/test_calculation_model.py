"""Integration tests for the Calculation model against a real PostgreSQL database."""

import pytest
from sqlalchemy.exc import IntegrityError

from app import crud
from app.database import SessionLocal
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationCreate
from app.schemas.user import UserCreate


@pytest.fixture
def user(db):
    return crud.create_user(
        db, UserCreate(username="alice", email="alice@example.com", password="SecurePass123")
    )


@pytest.mark.parametrize("calc_type, a, b, expected", [
    ("Add", 2, 3, 5),
    ("Sub", 10, 4, 6),
    ("Multiply", 3, 7, 21),
    ("Divide", 9, 2, 4.5),
])
def test_insert_calculation_stores_correct_data(db, user, calc_type, a, b, expected):
    created = crud.create_calculation(db, CalculationCreate(a=a, b=b, type=calc_type), user.id)

    # Read it back with a brand-new session to prove it is really in the database
    with SessionLocal() as fresh:
        stored = fresh.get(Calculation, created.id)
        assert stored.a == a
        assert stored.b == b
        assert stored.type == calc_type
        assert stored.result == expected
        assert stored.user_id == user.id
        assert stored.created_at is not None


def test_calculations_linked_to_user(db, user):
    crud.create_calculation(db, CalculationCreate(a=1, b=1, type="Add"), user.id)
    crud.create_calculation(db, CalculationCreate(a=2, b=2, type="Multiply"), user.id)

    results = crud.list_calculations_for_user(db, user.id)
    assert [c.result for c in results] == [2, 4]
    db.refresh(user)
    assert len(user.calculations) == 2
    assert results[0].user.username == "alice"
    assert crud.get_calculation(db, results[0].id).type == "Add"
    assert crud.get_calculation(db, 9999) is None


def test_foreign_key_rejects_missing_user(db):
    db.add(Calculation(a=1, b=2, type="Add", result=3, user_id=9999))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_database_rejects_invalid_type(db, user):
    db.add(Calculation(a=1, b=2, type="Modulo", result=1, user_id=user.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_database_rejects_zero_divisor(db, user):
    """Even if the schema were bypassed, the database blocks division by zero."""
    db.add(Calculation(a=1, b=0, type="Divide", result=None, user_id=user.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_deleting_user_deletes_their_calculations(db, user):
    calc = crud.create_calculation(db, CalculationCreate(a=5, b=5, type="Add"), user.id)
    calc_id = calc.id
    db.delete(db.get(User, user.id))
    db.commit()
    with SessionLocal() as fresh:
        assert fresh.get(Calculation, calc_id) is None