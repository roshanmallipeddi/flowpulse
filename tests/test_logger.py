from src.utils.logger import get_logger


def test_log_info():
    logger = get_logger("test_module")
    logger.info("This is an info log")


def test_log_to_file():
    logger = get_logger("test_module")
    logger.warning("This should appear in file")


def test_log_rotation_config():
    logger = get_logger("test_module")
    logger.error("Testing rotation configuration")


if __name__ == "__main__":
    test_log_info()
    test_log_to_file()
    test_log_rotation_config()