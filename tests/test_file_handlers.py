from src.utils.file_handlers import *

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
