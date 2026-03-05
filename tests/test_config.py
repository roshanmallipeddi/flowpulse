import pytest

from src.utils.config import ConfigError, ConfigKeyError, ConfigLoader


def test_load_config():
    config = ConfigLoader()
    assert config.get("project.name") == "FlowPulse"
    assert isinstance(config.get("database.port"), int)


def test_missing_key():
    config = ConfigLoader()
    with pytest.raises(ConfigKeyError):
        config.get("database.password")  # not in YAML


def test_env_override(monkeypatch):
    # YAML has database.port: 5432 (int). We'll override it with an env var string.
    monkeypatch.setenv("DATABASE_PORT", "6543")

    config = ConfigLoader()
    assert config.get("database.port") == 6543
    assert isinstance(config.get("database.port"), int)
    
def test_validate_required_lists_missing():
    config = ConfigLoader()
    with pytest.raises(ConfigError) as e:
        config.validate_required(["database.host", "database.password", "paths.raw_data"])

    # should mention the missing key
    assert "database.password" in str(e.value)