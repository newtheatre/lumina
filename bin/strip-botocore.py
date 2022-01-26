#!/usr/bin/env python3
import shutil
from pathlib import Path

KEEP = {"dynamodb", "ssm", "ses", "sesv2"}
BOTOCORE_DATA_PATH = Path(".aws-sam/build/PythonDependencyLayer/python/botocore/data")


def delete_unused_botocore_data():
    removed_dirs = set()
    for path in BOTOCORE_DATA_PATH.iterdir():
        if not path.is_dir():
            continue
        folder_name = path.name
        if folder_name not in KEEP:
            shutil.rmtree(path)
            removed_dirs.add(folder_name)
    print(f"Removed {len(removed_dirs)} botocore data directories: {removed_dirs}")


if __name__ == "__main__":
    delete_unused_botocore_data()
