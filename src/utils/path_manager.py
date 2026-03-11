from pathlib import Path
import shutil
from datetime import datetime

class PathManager:
    def __init__(self, project_root: Path = None):
        """
        Initializes the path manager.
        If project_root is not provided, it auto-detects it.
        """

        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = Path(project_root)
        self.raw_data_dir = self.project_root / "data" / "raw"
        self.processed_data_dir = self.project_root / "data" / "processed"
        self.output_dir = self.project_root / "output"
        self.logs_dir = self.project_root / "logs"
        self.config_dir = self.project_root / "config"
        self._ensure_directories()
    
    def _ensure_directories(self):
        directories = [
            self.raw_data_dir,
            self.processed_data_dir,
            self.output_dir,
            self.logs_dir,
            self.config_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def list_files(self, directory: Path, extension: str = None):
        directory = Path(directory)

        if extension:
            files = sorted([f for f in directory.glob(f"*.{extension}") if f.is_file()])
        else:
            files = sorted([f for f in directory.iterdir() if f.is_file()])
        return files  
    
    def get_latest_file(self, directory: Path, pattern: str):
        directory = Path(directory)

        files = list(directory.glob(pattern))

        if not files:
            return None

        latest = max(files, key=lambda f: f.stat().st_mtime)

        return latest   
    
    def archive_file(self, filepath: Path, archive_dir: Path):
        filepath = Path(filepath)
        archive_dir = Path(archive_dir)

        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{timestamp}_{filepath.name}"

        destination = archive_dir / new_name

        shutil.move(str(filepath), str(destination))

        return destination 
    
    def cleanup_old_files(self, directory: Path, days: int):
        directory = Path(directory)

        cutoff = datetime.now().timestamp() - (days * 86400)

        for file in directory.iterdir():
            if file.is_file():
                if file.stat().st_mtime < cutoff:
                    archive_dir = directory / "archive"
                    self.archive_file(file, archive_dir)