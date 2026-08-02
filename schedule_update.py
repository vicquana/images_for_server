import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path

import schedule


PROJECT_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = PROJECT_DIR / "biography_update_and_json_generation.py"
LOCK_PATH = PROJECT_DIR / ".biography_update.lock"


def run_script():
    print("Job started at:", time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        lock_descriptor = os.open(
            LOCK_PATH,
            os.O_CREAT | os.O_RDWR,
            0o600,
        )
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock_descriptor)
        print("Job skipped: another biography update is already running.")
        return

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=PROJECT_DIR,
            check=False,
        )
        if result.returncode == 0:
            print("Job completed successfully.")
        elif result.returncode == 2:
            print(
                "Job completed with partial results; any available updates "
                "were published."
            )
        else:
            print(f"Job failed with exit code {result.returncode}.")
    finally:
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        os.close(lock_descriptor)

    print("Job finished at:", time.strftime("%Y-%m-%d %H:%M:%S"))


schedule.every().monday.at("00:00").do(run_script)


if __name__ == "__main__":
    print("Schedule update service started...")
    print("Job holding at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    while True:
        schedule.run_pending()
        time.sleep(30)
