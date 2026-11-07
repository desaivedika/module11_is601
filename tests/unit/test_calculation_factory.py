"""Unit tests for the calculation factory."""

import pytest

from app.calculation_factory import (
    AddOperation,
    CalculationFactory,
    CalculationType,
    DivideOperation,
    MultiplyOperation,
    SubOperation,
)


@pytest.mark.parametrize("calc_type, expected_class", [
    (CalculationType.ADD, AddOperation),
    (CalculationType.SUB, SubOperation),
    (CalculationType.MULTIPLY, MultiplyOperation),
    (CalculationType.DIVIDE, DivideOperation),
    ("Add", AddOperation),
    ("Divide", DivideOperation),
])
def test_factory_chooses_correct_operation(calc_type, expected_class):
    assert isinstance(CalculationFactory.create(calc_type), expected_class)


@pytest.mark.parametrize("calc_type, a, b, expected", [
    ("Add", 10, 5, 15),
    ("Sub", 10, 5, 5),
    ("Multiply", 10, 5, 50),
    ("Divide", 10, 5, 2),
    ("Add", -2.5, 2.5, 0),
    ("Divide", 7, 2, 3.5),
])
def test_operations_compute_correct_result(calc_type, a, b, expected):
    assert CalculationFactory.create(calc_type).compute(a, b) == expected


def test_divide_by_zero_raises():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculationFactory.create("Divide").compute(1, 0)


@pytest.mark.parametrize("bad_type", ["Modulo", "add ", "", "Power"])
def test_unknown_type_raises(bad_type):
    with pytest.raises(ValueError, match="Unknown calculation type"):
        CalculationFactory.create(bad_type)