import csv
import json
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def read_csv(filepath, headers=None):
    """
    Read a CSV file and return list of dictionaries.
    If file doesn't exist, create an empty file with headers.
    """

    path = Path(filepath)

    if not path.exists():

        logger.warning(f"{filepath} not found. Creating empty CSV file.")

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8") as f:

            if headers:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()

        return []

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
    
def write_csv(data, filepath, headers=None):
    """
    Write list of dictionaries to CSV.
    """

    path = Path(filepath)

    path.parent.mkdir(parents=True, exist_ok=True)

    if not data:
        logger.warning("No data provided to write_csv")
        return

    if headers is None:
        headers = data[0].keys()

    with path.open(mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        writer.writeheader()
        writer.writerows(data)

    logger.info(f"CSV file written successfully: {filepath}")
    
def read_json(filepath):
    """
    Read JSON file and return dict or list.
    """

    path = Path(filepath)

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"JSON file read successfully: {filepath}")
        return data

    except FileNotFoundError:
        logger.warning(f"{filepath} not found. Creating empty JSON file.")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump({}, f)

        return {}

def write_json(data, filepath, indent=2):
    """
    Write data to JSON file.
    """

    path = Path(filepath)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)

    logger.info(f"JSON file written successfully: {filepath}")
    
def read_yaml(filepath):
    """
    Read YAML file. If file doesn't exist, create an empty YAML file.
    """

    path = Path(filepath)

    if not path.exists():

        logger.warning(f"{filepath} not found. Creating empty YAML file.")

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump({}, f)

        return {}

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data

def write_yaml(data, filepath):
    """
    Write data to YAML file.
    """

    path = Path(filepath)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    logger.info(f"YAML file written successfully: {filepath}")