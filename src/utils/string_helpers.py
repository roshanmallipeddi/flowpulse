import re

def clean_whitespace(text: str) -> str:
    """
    Removes leading/trailing whitespace and collapses multiple spaces into one.
    """

    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text

def normalize_case(text: str, mode: str = "lower") -> str:
    """
    Normalizes text case.
    Modes: lower, upper, title, sentence
    """

    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    mode = mode.lower()

    if mode == "lower":
        return text.lower()

    elif mode == "upper":
        return text.upper()

    elif mode == "title":
        return text.title()

    elif mode == "sentence":
        text = text.lower()
        return text.capitalize()

    else:
        raise ValueError("Invalid mode")
    
def extract_emails(text: str) -> list:
    """
    Extracts all email addresses from text.
    """

    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    pattern = r"[\w\.-]+@[\w\.-]+\.\w+"

    return re.findall(pattern, text)

def validate_phone(phone: str, country: str = "IN") -> bool:
    """
    Validates phone number for India or US.
    """

    if not isinstance(phone, str):
        return False

    phone = phone.strip()

    if country == "IN":
        pattern = r"^[6-9]\d{9}$"

    elif country == "US":
        pattern = r"^(\+1)?\d{10}$"

    else:
        raise ValueError("Unsupported country")

    return bool(re.match(pattern, phone))

def slugify(text: str) -> str:
    """
    Converts text into URL-safe slug.
    """

    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s-]", "", text)

    text = re.sub(r"\s+", "-", text)

    text = re.sub(r"-+", "-", text)

    return text.strip("-")