from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigError(Exception):
    """Base class for configuration-related errors."""


class ConfigFileNotFoundError(ConfigError):
    pass


class ConfigKeyError(ConfigError, KeyError):
    pass


@dataclass
class ConfigLoader:
    """
    Loads YAML config and supports:
    - nested dot access: get("database.host")
    - env var override: DATABASE_HOST overrides database.host
    - clear errors for missing required keys
    - required-key validation
    """

    config_path: str = "config/config.yaml"
    _config: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self._config = self._load_yaml(self.config_path)

    def _load_yaml(self, config_path: str) -> Dict[str, Any]:
        path = Path(config_path)
        if not path.exists():
            raise ConfigFileNotFoundError(f"Config file not found: {path.resolve()}")

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            # Empty YAML file
            return {}

        if not isinstance(data, dict):
            raise ConfigError("Top-level YAML content must be a mapping (dictionary).")

        return data

    def _env_key(self, dotted_key: str) -> str:
        # database.host -> DATABASE_HOST
        return dotted_key.upper().replace(".", "_")

    def _get_nested(self, dotted_key: str) -> Any:
        assert self._config is not None
        node: Any = self._config
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise ConfigKeyError(f"Missing required config key: '{dotted_key}'")
            node = node[part]
        return node

    def get(self, dotted_key: str, required: bool = True) -> Any:
        """
        Returns value for dotted_key.
        Priority:
          1) Environment variable override
          2) YAML value

        Note on typing:
          - YAML values come back typed (int/bool/str/etc.) automatically.
          - Env vars are strings; we cast them to the YAML type when possible.
        """
        env_key = self._env_key(dotted_key)
        env_val = os.getenv(env_key)

        if env_val is not None:
            # If YAML key exists, use it to infer type for casting.
            try:
                yaml_val = self._get_nested(dotted_key)
                return self._cast_env_value(env_val, type(yaml_val))
            except ConfigKeyError:
                # If YAML key doesn't exist but env var exists:
                # - if required=False, just return env string
                # - if required=True, we still allow env override to supply it
                return env_val

        # No env override: get from YAML
        try:
            return self._get_nested(dotted_key)
        except ConfigKeyError:
            if required:
                raise
            return None

    def _cast_env_value(self, raw: str, target_type: type) -> Any:
        """
        Cast env var string to match YAML type when possible.
        - bool: true/false/1/0/yes/no/on/off
        - int: "5432" -> 5432
        - float: "1.23" -> 1.23
        - str: keep as-is
        Otherwise: return raw string.
        """
        if target_type is bool:
            val = raw.strip().lower()
            if val in {"true", "1", "yes", "y", "on"}:
                return True
            if val in {"false", "0", "no", "n", "off"}:
                return False
            raise ConfigError(f"Cannot cast env value '{raw}' to bool.")

        if target_type is int:
            try:
                return int(raw.strip())
            except ValueError as e:
                raise ConfigError(f"Cannot cast env value '{raw}' to int.") from e

        if target_type is float:
            try:
                return float(raw.strip())
            except ValueError as e:
                raise ConfigError(f"Cannot cast env value '{raw}' to float.") from e

        if target_type is str:
            return raw

        # For types like list/dict/etc., keep env override as string
        return raw

    def validate_required(self, required_keys: List[str]) -> None:
        """
        Validate that all required keys exist (YAML or env override).
        If missing, raise one error listing all missing keys.
        """
        missing: List[str] = []
        for k in required_keys:
            try:
                _ = self.get(k, required=True)
            except ConfigKeyError:
                missing.append(k)

        if missing:
            # Clear, single error with everything listed
            raise ConfigError(
                "Missing required configuration keys: " + ", ".join(missing)
            )