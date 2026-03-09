import pytest
from datetime import datetime, timedelta, UTC
from pydantic import ValidationError

from src.models.schema import UserEvent, Transaction, Product, SystemTelemetry


# =========================
# UserEvent tests
# =========================

def test_valid_user_event():
    event = UserEvent(
        event_id="E1",
        user_id="U1",
        event_type="click",
        event_timestamp=datetime.now(UTC),
        metadata={"page": "home"}
    )
    assert event.user_id == "U1"
    assert event.event_type == "click"


def test_invalid_event_type():
    with pytest.raises(ValidationError):
        UserEvent(
            event_id="E2",
            user_id="U2",
            event_type="invalid",
            event_timestamp=datetime.now(UTC)
        )


def test_user_event_future_timestamp():
    with pytest.raises(ValidationError):
        UserEvent(
            event_id="E3",
            user_id="U3",
            event_type="view",
            event_timestamp=datetime.now(UTC) + timedelta(days=1)
        )


def test_user_event_empty_user_id():
    with pytest.raises(ValidationError):
        UserEvent(
            event_id="E4",
            user_id="   ",
            event_type="search",
            event_timestamp=datetime.now(UTC)
        )


# =========================
# Transaction tests
# =========================

def test_valid_transaction():
    tx = Transaction(
        transaction_id="T1",
        user_id="U1",
        product_id="P1",
        amount=120.50,
        status="completed",
        payment_method="card",
        timestamp=datetime.now(UTC)
    )
    assert tx.status == "completed"
    assert tx.amount == 120.50


def test_invalid_transaction_status():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="T2",
            user_id="U1",
            product_id="P1",
            amount=50.0,
            status="unknown",
            payment_method="card",
            timestamp=datetime.now(UTC)
        )


def test_invalid_payment_method():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="T3",
            user_id="U1",
            product_id="P1",
            amount=50.0,
            status="pending",
            payment_method="cash",
            timestamp=datetime.now(UTC)
        )


def test_refunded_transaction_must_have_negative_amount():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="T4",
            user_id="U1",
            product_id="P1",
            amount=100.0,
            status="refunded",
            payment_method="paypal",
            timestamp=datetime.now(UTC)
        )


def test_valid_refunded_transaction():
    tx = Transaction(
        transaction_id="T5",
        user_id="U1",
        product_id="P1",
        amount=-100.0,
        status="refunded",
        payment_method="paypal",
        timestamp=datetime.now(UTC)
    )
    assert tx.status == "refunded"
    assert tx.amount == -100.0


def test_non_refunded_transaction_cannot_have_negative_amount():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="T6",
            user_id="U1",
            product_id="P1",
            amount=-20.0,
            status="completed",
            payment_method="card",
            timestamp=datetime.now(UTC)
        )


# =========================
# Product tests
# =========================

def test_valid_product():
    product = Product(
        product_id="P1",
        name="Wireless Mouse",
        category="electronics",
        price=25.99,
        rating=4.5
    )
    assert product.category == "electronics"
    assert product.price == 25.99


def test_invalid_product_price():
    with pytest.raises(ValidationError):
        Product(
            product_id="P2",
            name="Book",
            category="books",
            price=0,
            rating=4.0
        )


def test_invalid_product_rating():
    with pytest.raises(ValidationError):
        Product(
            product_id="P3",
            name="T-Shirt",
            category="clothing",
            price=15.0,
            rating=5.5
        )


def test_invalid_product_category():
    with pytest.raises(ValidationError):
        Product(
            product_id="P4",
            name="Desk Lamp",
            category="furniture",
            price=30.0,
            rating=4.2
        )


# =========================
# SystemTelemetry tests
# =========================

def test_valid_system_telemetry():
    telemetry = SystemTelemetry(
        metric_id="M1",
        metric_name="cpu_usage",
        metric_value=72.5,
        severity="medium",
        timestamp=datetime.now(UTC)
    )
    assert telemetry.severity == "medium"
    assert telemetry.metric_value == 72.5


def test_invalid_telemetry_severity():
    with pytest.raises(ValidationError):
        SystemTelemetry(
            metric_id="M2",
            metric_name="memory_usage",
            metric_value=64.0,
            severity="urgent",
            timestamp=datetime.now(UTC)
        )


def test_invalid_telemetry_metric_value():
    with pytest.raises(ValidationError):
        SystemTelemetry(
            metric_id="M3",
            metric_name="disk_usage",
            metric_value=-1.0,
            severity="low",
            timestamp=datetime.now(UTC)
        )


# =========================
# Cross-model tests
# =========================

def test_user_event_to_dict():
    event = UserEvent(
        event_id="E10",
        user_id="U10",
        event_type="view",
        event_timestamp=datetime.now(UTC),
        metadata={"source": "app"}
    )
    data = event.to_dict()
    assert isinstance(data, dict)
    assert data["event_id"] == "E10"


def test_product_from_dict():
    data = {
        "product_id": "P10",
        "name": "Notebook",
        "category": "books",
        "price": 10.5,
        "rating": 4.1
    }
    product = Product.from_dict(data)
    assert isinstance(product, Product)
    assert product.name == "Notebook"


def test_system_telemetry_to_from_dict_roundtrip():
    telemetry = SystemTelemetry(
        metric_id="M10",
        metric_name="network_latency",
        metric_value=12.4,
        severity="low",
        timestamp=datetime.now(UTC)
    )
    data = telemetry.to_dict()
    rebuilt = SystemTelemetry.from_dict(data)
    assert rebuilt.metric_id == telemetry.metric_id
    assert rebuilt.metric_value == telemetry.metric_value
    assert rebuilt.severity == telemetry.severity