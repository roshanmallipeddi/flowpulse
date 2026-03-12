import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BatchFileProcessor:
    def __init__(self, file_paths, process_function, max_workers=5):
        self.file_paths = file_paths
        self.process_function = process_function
        self.max_workers = max_workers

        self.files_processed = 0
        self.files_failed = 0

    def _process_single_file(self, file_path):
        start = time.time()
        result = self.process_function(file_path)
        end = time.time()
        duration = end - start
        return file_path, result, duration

    def process_all(self):
        self.files_processed = 0
        self.files_failed = 0

        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path
                for file_path in self.file_paths
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]

                try:
                    processed_file, result, duration = future.result()
                    self.files_processed += 1
                    logger.info(f"Processed {processed_file} in {duration:.4f}s")
                    results.append(result)

                except Exception as e:
                    self.files_failed += 1
                    logger.error(f"Failed processing {file_path}: {e}")

        total_time = time.time() - start_time

        return {
            "files_total": len(self.file_paths),
            "files_processed": self.files_processed,
            "files_failed": self.files_failed,
            "total_time": round(total_time, 4),
            "results": results,
        }


def process_csv(file_path):
    count = 0

    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for _ in reader:
            count += 1

    return {
        "file": file_path,
        "rows": count,
    }


if __name__ == "__main__":
    files = [
        "data/raw/events_1.csv",
        "data/raw/events_2.csv",
        "data/raw/events_3.csv",
        "data/raw/events_4.csv",
        "data/raw/events_5.csv",
    ]

    processor = BatchFileProcessor(files, process_csv)
    summary = processor.process_all()
    logger.info(f"Batch summary: {summary}")