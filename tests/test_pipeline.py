import subprocess
import unittest
from unittest.mock import call, patch

import biography_update_and_json_generation as pipeline
from update_biography import BiographyUpdateResult


class PipelineTests(unittest.TestCase):
    def test_partial_results_are_committed_and_pushed(self):
        result = BiographyUpdateResult(
            total=3,
            updated=["alpha"],
            unchanged=["gamma"],
            failed={"beta": "400 Bad Request"},
        )

        with patch.object(
            pipeline,
            "run_git_command",
            side_effect=[
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 1),
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 0),
            ],
        ) as run_git_command:
            published = pipeline.publish_updates(result)

        self.assertTrue(published)
        paths = ["alpha/biography.txt", "data.json"]
        self.assertEqual(
            run_git_command.call_args_list,
            [
                call(["add", "--", *paths]),
                call(
                    ["diff", "--cached", "--quiet", "--", *paths],
                    check=False,
                ),
                call(
                    [
                        "commit",
                        "--only",
                        "-m",
                        "update biographies and json database "
                        "(1 updated, 1 failed)",
                        "--",
                        *paths,
                    ]
                ),
                call(["push"]),
            ],
        )

    def test_no_changed_output_does_not_commit_or_push(self):
        result = BiographyUpdateResult(total=1, unchanged=["alpha"])

        with patch.object(
            pipeline,
            "run_git_command",
            side_effect=[
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 0),
            ],
        ) as run_git_command:
            published = pipeline.publish_updates(result)

        self.assertFalse(published)
        self.assertEqual(run_git_command.call_count, 2)


if __name__ == "__main__":
    unittest.main()
