import json
from pathlib import Path
import pytest
import yaml

from src.utils.file_handlers import (
    read_csv,
    write_csv,
    read_json,
    write_json,
    read_yaml,
    write_yaml,
)

def test_read_csv():

    data = read_csv("data/raw/sample_events.csv")

    assert isinstance(data, list)
    assert len(data) > 0
    
def test_write_csv():

    data = [
        {"id":1,"name":"A"},
        {"id":2,"name":"B"}
    ]

    write_csv(data,"data/raw/test.csv")

    assert True
    
def test_read_json():

    data = read_json("data/raw/sample_products.json")

    assert isinstance(data, list)
    
def test_write_json():

    data = {"name":"flowpulse"}

    write_json(data,"data/raw/test.json")

    assert True

def test_read_yaml():

    data = read_yaml("data/raw/sample_config.yaml")

    assert isinstance(data, dict)

def test_write_yaml():

    data = {"pipeline":"flowpulse"}

    write_yaml(data,"data/raw/test.yaml")

    assert True

def test_read_csv_creates_file():

    data = read_csv(
        "data/raw/missing.csv",
        headers=["id", "name"]
    )

    assert data == []
    
def test_write_csv_then_read():

    data = [
        {"id": 1, "name": "apple"},
        {"id": 2, "name": "banana"}
    ]

    filepath = "data/raw/test_roundtrip.csv"

    write_csv(data, filepath)

    result = read_csv(filepath)

    assert len(result) == 2
    
def test_read_json_creates_file():

    data = read_json("data/raw/missing.json")

    assert data == {}

def test_write_json_then_read():

    data = {"project": "flowpulse"}

    filepath = "data/raw/test_roundtrip.json"

    write_json(data, filepath)

    result = read_json(filepath)

    assert result["project"] == "flowpulse"

def test_read_yaml_creates_file():

    data = read_yaml("data/raw/missing.yaml")

    assert data == {}

def test_write_yaml_then_read():

    data = {"pipeline": "flowpulse"}

    filepath = "data/raw/test_roundtrip.yaml"

    write_yaml(data, filepath)

    result = read_yaml(filepath)

    assert result["pipeline"] == "flowpulse"

def test_read_csv_missing_file_without_headers_returns_empty_list(tmp_path):
    file_path = tmp_path / "missing" / "data.csv"

    result = read_csv(file_path)

    assert result == []
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == ""


def test_read_csv_missing_file_with_headers_creates_header_row(tmp_path):
    file_path = tmp_path / "missing_with_headers" / "data.csv"

    result = read_csv(file_path, headers=["id", "name"])

    assert result == []
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")
    assert "id,name" in content


def test_write_csv_with_empty_data_creates_directory_but_writes_nothing(tmp_path):
    file_path = tmp_path / "empty_case" / "data.csv"

    write_csv([], file_path)

    assert file_path.parent.exists()
    assert not file_path.exists()


def test_write_csv_uses_first_row_keys_when_headers_not_provided(tmp_path):
    file_path = tmp_path / "auto_headers" / "data.csv"
    data = [
        {"id": 1, "name": "Roshan"},
        {"id": 2, "name": "FlowPulse"},
    ]

    write_csv(data, file_path)

    assert file_path.exists()
    loaded = read_csv(file_path)
    assert len(loaded) == 2
    assert loaded[0]["name"] == "Roshan"


def test_read_json_missing_file_creates_empty_json_and_returns_empty_dict(tmp_path):
    file_path = tmp_path / "missing_json" / "data.json"

    result = read_json(file_path)

    assert result == {}
    assert file_path.exists()

    with file_path.open("r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved == {}


def test_write_json_creates_nested_directories(tmp_path):
    file_path = tmp_path / "deep" / "nested" / "data.json"
    data = {"project": "FlowPulse", "day": 7}

    write_json(data, file_path)

    assert file_path.exists()
    assert read_json(file_path) == data


def test_read_yaml_missing_file_creates_empty_yaml_and_returns_empty_dict(tmp_path):
    file_path = tmp_path / "missing_yaml" / "data.yaml"

    result = read_yaml(file_path)

    assert result == {}
    assert file_path.exists()

    with file_path.open("r", encoding="utf-8") as f:
        saved = yaml.safe_load(f)

    assert saved == {}


def test_write_yaml_creates_nested_directories(tmp_path):
    file_path = tmp_path / "deep_yaml" / "nested" / "data.yaml"
    data = {"status": "ok", "count": 2}

    write_yaml(data, file_path)

    assert file_path.exists()
    assert read_yaml(file_path) == data