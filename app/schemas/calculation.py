"""Pydantic schemas for creating and reading calculations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, field_validator, model_validator

from app.calculation_factory import CalculationType


class CalculationCreate(BaseModel):
    """Data needed to create a calculation: two numbers and a type."""

    a: FiniteFloat = Field(examples=[10])
    b: FiniteFloat = Field(examples=[5])
    type: CalculationType = Field(examples=["Add"])

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        """Accept the type in any letter case, e.g. 'add', 'ADD' or 'Add'."""
        if isinstance(value, str):
            for calc_type in CalculationType:
                if value.strip().lower() == calc_type.value.lower():
                    return calc_type
        return value  # Pydantic reports a clear error for anything else

    @model_validator(mode="after")
    def no_zero_divisor(self) -> "CalculationCreate":
        """Reject division by zero before it ever reaches the database."""
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero: b must not be 0 for Divide")
        return self


class CalculationRead(BaseModel):
    """Data returned for a calculation. Contains no user details."""

    id: int
    a: float
    b: float
    type: CalculationType
    result: float | None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)