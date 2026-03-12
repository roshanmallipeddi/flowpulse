import csv
import time
from pathlib import Path

from src.pipeline.batch_processor import BatchFileProcessor


def create_csv_file(file_path: Path, rows: int = 100) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "event_type", "event_time"])

        for i in range(rows):
            writer.writerow([i + 1, "login", "2026-03-12T10:00:00"])


def process_csv(file_path):
    count = 0

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for _ in reader:
            count += 1

    return {
        "file": str(file_path),
        "rows": count
    }


def slow_process_csv(file_path):
    time.sleep(0.1)
    return process_csv(file_path)


def test_process_all_succeeds(tmp_path):
    files = []

    for i in range(5):
        file_path = tmp_path / f"events_{i+1}.csv"
        create_csv_file(file_path)
        files.append(str(file_path))

    processor = BatchFileProcessor(files, process_csv, max_workers=5)
    summary = processor.process_all()

    assert summary["files_total"] == 5
    assert summary["files_processed"] == 5
    assert summary["files_failed"] == 0
    assert len(summary["results"]) == 5

    for result in summary["results"]:
        assert result["rows"] == 100


def test_handles_missing_file(tmp_path):
    valid_file = tmp_path / "events_1.csv"
    create_csv_file(valid_file)

    missing_file = tmp_path / "missing.csv"

    files = [str(valid_file), str(missing_file)]

    processor = BatchFileProcessor(files, process_csv, max_workers=2)
    summary = processor.process_all()

    assert summary["files_total"] == 2
    assert summary["files_processed"] == 1
    assert summary["files_failed"] == 1
    assert len(summary["results"]) == 1
    assert summary["results"][0]["rows"] == 100


def test_parallel_faster_than_sequential(tmp_path):
    files = []

    for i in range(5):
        file_path = tmp_path / f"events_{i+1}.csv"
        create_csv_file(file_path)
        files.append(str(file_path))

    sequential_start = time.perf_counter()
    for file_path in files:
        slow_process_csv(file_path)
    sequential_time = time.perf_counter() - sequential_start

    processor = BatchFileProcessor(files, slow_process_csv, max_workers=5)

    parallel_start = time.perf_counter()
    summary = processor.process_all()
    parallel_time = time.perf_counter() - parallel_start

    assert summary["files_processed"] == 5
    assert summary["files_failed"] == 0
    assert parallel_time < sequential_time


def test_max_workers_config(tmp_path):
    files = []

    for i in range(3):
        file_path = tmp_path / f"events_{i+1}.csv"
        create_csv_file(file_path)
        files.append(str(file_path))

    processor = BatchFileProcessor(files, process_csv, max_workers=3)

    assert processor.max_workers == 3