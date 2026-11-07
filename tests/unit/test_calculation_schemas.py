"""Unit tests for the calculation schemas and model helpers (no database)."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.calculation_factory import CalculationType
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationRead


def test_valid_calculation_create():
    calc = CalculationCreate(a=10, b=5, type="Add")
    assert calc.a == 10 and calc.b == 5
    assert calc.type == CalculationType.ADD


@pytest.mark.parametrize("raw, expected", [
    ("add", CalculationType.ADD),
    ("SUB", CalculationType.SUB),
    (" multiply ", CalculationType.MULTIPLY),
    ("Divide", CalculationType.DIVIDE),
])
def test_type_is_case_insensitive(raw, expected):
    assert CalculationCreate(a=1, b=2, type=raw).type == expected


@pytest.mark.parametrize("bad_type", ["Modulo", "Addition", "", 5, None])
def test_invalid_type_rejected(bad_type):
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=2, type=bad_type)


def test_zero_divisor_rejected():
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationCreate(a=10, b=0, type="Divide")


def test_zero_b_allowed_for_other_types():
    assert CalculationCreate(a=10, b=0, type="Multiply").b == 0


@pytest.mark.parametrize("field, value", [
    ("a", "ten"),
    ("b", None),
    ("a", float("inf")),
    ("b", float("nan")),
])
def test_invalid_operands_rejected(field, value):
    data = {"a": 1, "b": 2, "type": "Add", field: value}
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


def test_missing_field_rejected():
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, type="Add")


def test_calculation_read_from_orm_object():
    calc = Calculation(id=7, a=6, b=3, type="Divide", result=2.0, user_id=1,
                       created_at=datetime.now(timezone.utc))
    data = CalculationRead.model_validate(calc).model_dump()
    assert data["id"] == 7
    assert data["type"] == CalculationType.DIVIDE
    assert data["result"] == 2.0
    assert set(data) == {"id", "a", "b", "type", "result", "user_id", "created_at"}


def test_model_compute_result_uses_factory():
    calc = Calculation(a=4, b=5, type="Multiply", user_id=1)
    assert calc.compute_result() == 20
    assert "Multiply" in repr(calc)