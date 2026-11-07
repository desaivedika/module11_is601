"""Factory pattern for calculation logic.

Each calculation type (Add, Sub, Multiply, Divide) has its own operation class.
CalculationFactory picks the right class from a type, so no other code needs
a long if/elif chain. Adding a new type only means adding one class and one
registry entry.
"""

from abc import ABC, abstractmethod
from enum import Enum

from app import operations


class CalculationType(str, Enum):
    """The supported calculation types."""

    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class Operation(ABC):
    """Base class for one calculation type."""

    @abstractmethod
    def compute(self, a: float, b: float) -> float:
        """Return the result of applying this operation to a and b."""


class AddOperation(Operation):
    """a + b"""

    def compute(self, a: float, b: float) -> float:
        return operations.add(a, b)


class SubOperation(Operation):
    """a - b"""

    def compute(self, a: float, b: float) -> float:
        return operations.subtract(a, b)


class MultiplyOperation(Operation):
    """a * b"""

    def compute(self, a: float, b: float) -> float:
        return operations.multiply(a, b)


class DivideOperation(Operation):
    """a / b (raises ValueError when b is zero)"""

    def compute(self, a: float, b: float) -> float:
        return operations.divide(a, b)


class CalculationFactory:
    """Creates the correct Operation for a calculation type."""

    _registry: dict[CalculationType, type[Operation]] = {
        CalculationType.ADD: AddOperation,
        CalculationType.SUB: SubOperation,
        CalculationType.MULTIPLY: MultiplyOperation,
        CalculationType.DIVIDE: DivideOperation,
    }

    @classmethod
    def create(cls, calc_type: "CalculationType | str") -> Operation:
        """Return an Operation instance for calc_type. Raises ValueError if unknown."""
        try:
            key = CalculationType(calc_type)
        except ValueError as exc:
            allowed = ", ".join(t.value for t in CalculationType)
            raise ValueError(f"Unknown calculation type '{calc_type}'. Use one of: {allowed}") from exc
        return cls._registry[key]()