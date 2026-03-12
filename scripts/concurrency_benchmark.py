import csv
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


def create_csv_file(file_path, rows=100):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "event_type", "event_time"])

        for i in range(rows):
            writer.writerow([i + 1, "login", "2026-03-12T10:00:00"])


def process_csv_with_delay(file_path):
    count = 0

    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for _ in reader:
            count += 1

    time.sleep(0.1)  # simulate I/O wait
    return {"file": str(file_path), "rows": count}


def run_with_executor(executor_class, file_paths, max_workers=5):
    start = time.perf_counter()

    with executor_class(max_workers=max_workers) as executor:
        futures = [executor.submit(process_csv_with_delay, file_path) for file_path in file_paths]
        results = [future.result() for future in as_completed(futures)]

    total_time = time.perf_counter() - start
    return total_time, results


if __name__ == "__main__":
    files = []

    for i in range(10):
        file_path = Path("data/raw") / f"benchmark_events_{i+1}.csv"
        create_csv_file(file_path)
        files.append(str(file_path))

    sequential_start = time.perf_counter()
    for file_path in files:
        process_csv_with_delay(file_path)
    sequential_time = time.perf_counter() - sequential_start

    thread_time, _ = run_with_executor(ThreadPoolExecutor, files, max_workers=5)
    process_time, _ = run_with_executor(ProcessPoolExecutor, files, max_workers=5)

    print("\nBenchmark Results")
    print("-" * 50)
    print(f"{'Method':<20}{'Total Time':<15}{'Speedup'}")
    print("-" * 50)
    print(f"{'Sequential':<20}{sequential_time:<15.4f}{1.00:.2f}x")
    print(f"{'Threading':<20}{thread_time:<15.4f}{sequential_time / thread_time:.2f}x")
    print(f"{'Multiprocessing':<20}{process_time:<15.4f}{sequential_time / process_time:.2f}x")