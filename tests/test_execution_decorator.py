from src.utils.logger import log_execution_time


@log_execution_time
def sample_task():
    total = 0
    for i in range(1000000):
        total += i
    return total


if __name__ == "__main__":
    sample_task()