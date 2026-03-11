from pathlib import Path
import time

from src.utils.path_manager import PathManager

def test_init_creates_dirs(tmp_path):
    pm = PathManager(project_root=tmp_path)

    assert pm.raw_data_dir.exists()
    assert pm.processed_data_dir.exists()
    assert pm.output_dir.exists()
    assert pm.logs_dir.exists()
    assert pm.config_dir.exists()
    
def test_get_latest_file(tmp_path):
    pm = PathManager(project_root=tmp_path)

    file1 = pm.raw_data_dir / "old_file.csv"
    file2 = pm.raw_data_dir / "new_file.csv"

    file1.write_text("old")
    time.sleep(1)
    file2.write_text("new")

    latest = pm.get_latest_file(pm.raw_data_dir, "*.csv")

    assert latest == file2
    
def test_archive_file(tmp_path):
    pm = PathManager(project_root=tmp_path)

    original_file = pm.raw_data_dir / "sample.csv"
    original_file.write_text("test data")

    archive_dir = pm.raw_data_dir / "archive"

    archived_file = pm.archive_file(original_file, archive_dir)

    assert not original_file.exists()
    assert archived_file.exists()
    assert archived_file.parent == archive_dir
    assert archived_file.name.endswith("sample.csv")
    
def test_list_files(tmp_path):
    pm = PathManager(project_root=tmp_path)

    file1 = pm.raw_data_dir / "b.csv"
    file2 = pm.raw_data_dir / "a.csv"
    file3 = pm.raw_data_dir / "notes.txt"

    file1.write_text("1")
    file2.write_text("2")
    file3.write_text("3")

    csv_files = pm.list_files(pm.raw_data_dir, "csv")

    assert csv_files == [file2, file1]
    
def test_config_integration(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config.yaml"
    config_file.write_text(
        """
paths:
  raw_data_dir: data/raw
  processed_data_dir: data/processed
  output_dir: output
  logs_dir: logs
  config_dir: config
archive:
  cleanup_days: 30
""".strip()
    )

    pm = PathManager(project_root=tmp_path)

    assert pm.config_dir == tmp_path / "config"
    assert pm.raw_data_dir == tmp_path / "data" / "raw"
    assert pm.processed_data_dir == tmp_path / "data" / "processed"
    assert pm.output_dir == tmp_path / "output"
    assert pm.logs_dir == tmp_path / "logs"
    