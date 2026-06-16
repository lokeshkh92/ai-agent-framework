import csv
import os
from datetime import datetime
from typing import Any, Dict, List


class FileService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def write_csv(self, rows: List[Dict[str, Any]], file_prefix: str, sub_dir: str = "") -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        target_dir = os.path.join(self.base_dir, sub_dir)
        os.makedirs(target_dir, exist_ok=True)

        file_path = os.path.join(target_dir, f"{file_prefix}_{timestamp}.csv")

        if not rows:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["message"])
                writer.writerow(["No rows returned"])
            return file_path

        fieldnames = sorted({key for row in rows for key in row.keys()})

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        return file_path
