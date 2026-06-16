import subprocess
from typing import Dict, List


class HDFSService:
    def list_files(self, hdfs_path: str) -> Dict:
        cmd = ["hdfs", "dfs", "-ls", hdfs_path]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return {
                    "path": hdfs_path,
                    "exists": False,
                    "file_count": 0,
                    "files": [],
                    "stderr": result.stderr.strip(),
                }

            files: List[str] = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 8:
                    files.append(parts[-1])

            return {
                "path": hdfs_path,
                "exists": True,
                "file_count": len(files),
                "files": files,
                "stderr": "",
            }

        except Exception as exc:
            return {
                "path": hdfs_path,
                "exists": False,
                "file_count": 0,
                "files": [],
                "stderr": str(exc),
            }
