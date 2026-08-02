import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import schedule_update


class ScheduleUpdateTests(unittest.TestCase):
    def test_partial_result_releases_process_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / ".biography_update.lock"

            with (
                patch.object(schedule_update, "LOCK_PATH", lock_path),
                patch.object(
                    schedule_update.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 2),
                ) as run,
            ):
                schedule_update.run_script()
                schedule_update.run_script()

            self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
