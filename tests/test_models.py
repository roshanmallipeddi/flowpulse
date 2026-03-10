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
    
# =========================
# Additional gap-filling tests
# =========================

def test_product_rating_lower_boundary():
    product = Product(
        product_id="P20",
        name="Budget Pen",
        category="books",
        price=1.5,
        rating=1.0
    )
    assert product.rating == 1.0


def test_product_rating_upper_boundary():
    product = Product(
        product_id="P21",
        name="Premium Headphones",
        category="electronics",
        price=199.99,
        rating=5.0
    )
    assert product.rating == 5.0


def test_product_missing_required_name():
    with pytest.raises(ValidationError):
        Product(
            product_id="P22",
            category="books",
            price=10.0,
            rating=4.0
        )


def test_product_invalid_price_type():
    with pytest.raises(ValidationError):
        Product(
            product_id="P23",
            name="Notebook",
            category="books",
            price="cheap",
            rating=4.0
        )


def test_transaction_missing_required_status():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="T20",
            user_id="U1",
            product_id="P1",
            amount=50.0,
            payment_method="card",
            timestamp=datetime.now(UTC)
        )


def test_transaction_invalid_amount_type():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="T21",
            user_id="U1",
            product_id="P1",
            amount="fifty",
            status="pending",
            payment_method="card",
            timestamp=datetime.now(UTC)
        )


def test_user_event_missing_required_event_type():
    with pytest.raises(ValidationError):
        UserEvent(
            event_id="E20",
            user_id="U20",
            event_timestamp=datetime.now(UTC)
        )


def test_system_telemetry_missing_required_metric_name():
    with pytest.raises(ValidationError):
        SystemTelemetry(
            metric_id="M20",
            metric_value=50.0,
            severity="low",
            timestamp=datetime.now(UTC)
        )


def test_transaction_to_from_dict_roundtrip():
    tx = Transaction(
        transaction_id="T30",
        user_id="U30",
        product_id="P30",
        amount=89.99,
        status="completed",
        payment_method="card",
        timestamp=datetime.now(UTC)
    )
    data = tx.to_dict()
    rebuilt = Transaction.from_dict(data)

    assert rebuilt.transaction_id == tx.transaction_id
    assert rebuilt.user_id == tx.user_id
    assert rebuilt.product_id == tx.product_id
    assert rebuilt.amount == tx.amount
    assert rebuilt.status == tx.status
    assert rebuilt.payment_method == tx.payment_method


def test_user_event_to_from_dict_roundtrip():
    event = UserEvent(
        event_id="E30",
        user_id="U30",
        event_type="purchase",
        event_timestamp=datetime.now(UTC),
        metadata={"item": "keyboard"}
    )
    data = event.to_dict()
    rebuilt = UserEvent.from_dict(data)

    assert rebuilt.event_id == event.event_id
    assert rebuilt.user_id == event.user_id
    assert rebuilt.event_type == event.event_type
    assert rebuilt.metadata == event.metadata    