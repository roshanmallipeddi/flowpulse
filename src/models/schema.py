from datetime import datetime, UTC
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


ALLOWED_EVENT_TYPES = {"click", "view", "purchase", "search"}
ALLOWED_TRANSACTION_STATUS = {"completed", "pending", "failed", "refunded"}
ALLOWED_PAYMENT_METHODS = {"card", "paypal", "bank_transfer"}
ALLOWED_PRODUCT_CATEGORIES = {"electronics", "clothing", "home", "books"}
ALLOWED_SEVERITY = {"low", "medium", "high", "critical"}


class UserEvent(BaseModel):
    event_id: str
    user_id: str
    event_type: str
    event_timestamp: datetime
    metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": "E1001",
                "user_id": "U001",
                "event_type": "click",
                "event_timestamp": "2026-03-09T10:00:00",
                "metadata": {"page": "home"},
            }
        }
    )

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        if value not in ALLOWED_EVENT_TYPES:
            raise ValueError("Invalid event_type")
        return value

    @field_validator("event_timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value > datetime.now(UTC):
            raise ValueError("event_timestamp cannot be in the future")
        return value

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("user_id cannot be empty")
        return value

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "UserEvent":
        return cls(**data)


class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    product_id: str
    amount: float
    status: str
    payment_method: str
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_id": "T1001",
                "user_id": "U001",
                "product_id": "P001",
                "amount": 499.99,
                "status": "completed",
                "payment_method": "card",
                "timestamp": "2026-03-09T14:00:00",
            }
        }
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in ALLOWED_TRANSACTION_STATUS:
            raise ValueError("Invalid status")
        return value

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: str) -> str:
        if value not in ALLOWED_PAYMENT_METHODS:
            raise ValueError("Invalid payment_method")
        return value

    @model_validator(mode="after")
    def validate_amount_rules(self) -> "Transaction":
        if self.status == "refunded":
            if self.amount >= 0:
                raise ValueError("Refunded transactions must have negative amount")
        else:
            if self.amount < 0:
                raise ValueError("amount must be >= 0 for non-refunded transactions")
        return self

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(**data)


class Product(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    rating: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "P001",
                "name": "Wireless Mouse",
                "category": "electronics",
                "price": 25.99,
                "rating": 4.5,
            }
        }
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in ALLOWED_PRODUCT_CATEGORIES:
            raise ValueError("Invalid category")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("price must be > 0")
        return value

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: float) -> float:
        if not (1.0 <= value <= 5.0):
            raise ValueError("rating must be between 1.0 and 5.0")
        return value

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(**data)


class SystemTelemetry(BaseModel):
    metric_id: str
    metric_name: str
    metric_value: float
    severity: str
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metric_id": "M001",
                "metric_name": "cpu_usage",
                "metric_value": 73.4,
                "severity": "medium",
                "timestamp": "2026-03-09T16:00:00",
            }
        }
    )

    @field_validator("metric_value")
    @classmethod
    def validate_metric_value(cls, value: float) -> float:
        if value < 0:
            raise ValueError("metric_value must be >= 0")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        if value not in ALLOWED_SEVERITY:
            raise ValueError("Invalid severity")
        return value

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "SystemTelemetry":
        return cls(**data)