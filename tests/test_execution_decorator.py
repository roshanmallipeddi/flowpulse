import os
import time

from src.utils.logger import log_execution_time


def test_log_execution_time_writes_to_log_file():
    @log_execution_time
    def greet():
        time.sleep(0.01)
        return "hello"

    result = greet()
    assert result == "hello"

    log_file = os.path.join("logs", "flowpulse.log")
    assert os.path.exists(log_file)

    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "greet executed in" in content


def test_log_execution_time_returns_original_result():
    @log_execution_time
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5


def test_log_execution_time_preserves_function_metadata():
    @log_execution_time
    def sample_function():
        """sample docstring"""
        return "ok"

    assert sample_function.__name__ == "sample_function"
    assert sample_function.__doc__ == "sample docstring"