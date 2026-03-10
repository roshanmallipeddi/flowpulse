import pytest

from src.utils.string_helpers import (
    clean_whitespace,
    normalize_case,
    extract_emails,
    validate_phone,
    slugify,
)

def test_clean_whitespace_normal():
    assert clean_whitespace("  hello   world  ") == "hello world"


def test_clean_whitespace_single_word():
    assert clean_whitespace("   python   ") == "python"


def test_clean_whitespace_empty():
    assert clean_whitespace("     ") == ""
    
def test_normalize_lower():
    assert normalize_case("HELLO", "lower") == "hello"


def test_normalize_upper():
    assert normalize_case("hello", "upper") == "HELLO"


def test_normalize_title():
    assert normalize_case("hello world", "title") == "Hello World"
    
def test_extract_single_email():
    text = "Contact me at test@gmail.com"
    assert extract_emails(text) == ["test@gmail.com"]


def test_extract_multiple_emails():
    text = "a@test.com b@test.org"
    assert extract_emails(text) == ["a@test.com", "b@test.org"]


def test_extract_no_email():
    assert extract_emails("hello world") == []
    
def test_validate_indian_phone():
    assert validate_phone("9876543210", "IN") is True


def test_validate_us_phone():
    assert validate_phone("+11234567890", "US") is True


def test_invalid_phone():
    assert validate_phone("12345", "IN") is False
    
def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_numbers():
    assert slugify("Hello World 123") == "hello-world-123"


def test_slugify_special_chars():
    assert slugify("Hello@World!!!") == "helloworld"
    
def test_clean_whitespace_invalid_input():
    with pytest.raises(ValueError, match="Input must be a string"):
        clean_whitespace(None)


def test_normalize_case_invalid_input():
    with pytest.raises(ValueError, match="Input must be a string"):
        normalize_case(123)


def test_normalize_sentence_case():
    result = normalize_case("hELLo worLD", mode="sentence")
    assert result == "Hello world"


def test_normalize_case_invalid_mode():
    with pytest.raises(ValueError, match="Invalid mode"):
        normalize_case("hello world", mode="camel")


def test_extract_emails_invalid_input():
    with pytest.raises(ValueError, match="Input must be a string"):
        extract_emails(["test@example.com"])


def test_validate_phone_unsupported_country():
    with pytest.raises(ValueError, match="Unsupported country"):
        validate_phone("9876543210", country="UK")


def test_slugify_invalid_input():
    with pytest.raises(ValueError, match="Input must be a string"):
        slugify(None)