import csv
import random
from datetime import datetime
from pathlib import Path


def generate_user_events(num_files=5, rows_per_file=100):
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    events = ["login", "logout", "click", "purchase"]

    for i in range(1, num_files + 1):
        file_path = output_dir / f"events_{i}.csv"

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "event_type", "event_time"])

            for _ in range(rows_per_file):
                writer.writerow([
                    random.randint(1, 100),
                    random.choice(events),
                    datetime.utcnow().isoformat()
                ])

    print(f"Generated {num_files} files in {output_dir}")


if __name__ == "__main__":
    generate_user_events()