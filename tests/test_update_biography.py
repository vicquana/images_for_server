import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import instaloader

import update_biography


class BiographyUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.loader = SimpleNamespace(context=object())

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_account(self, name: str, biography: str) -> Path:
        account_directory = self.root / name
        account_directory.mkdir()
        biography_path = account_directory / "biography.txt"
        biography_path.write_text(biography, encoding="utf-8")
        return biography_path

    def test_continues_after_non_blocking_failure_and_preserves_old_biography(self):
        alpha_path = self.create_account("alpha", "old alpha")
        beta_path = self.create_account("beta", "old beta")
        self.create_account("gamma", "same gamma")
        waits = []

        responses = {
            "alpha": SimpleNamespace(biography="new alpha"),
            "beta": instaloader.exceptions.BadResponseException(
                "400 Bad Request: deleted schema"
            ),
            "gamma": SimpleNamespace(biography="same gamma"),
        }

        def profile_response(_context, username):
            response = responses[username]
            if isinstance(response, Exception):
                raise response
            return response

        with patch.object(
            update_biography.instaloader.Profile,
            "from_username",
            side_effect=profile_response,
        ):
            result = update_biography.update_biography(
                self.root,
                loader=self.loader,
                sleep_fn=waits.append,
            )

        self.assertEqual(result.updated, ["alpha"])
        self.assertEqual(result.unchanged, ["gamma"])
        self.assertEqual(list(result.failed), ["beta"])
        self.assertFalse(result.stopped_early)
        self.assertFalse(result.blocked)
        self.assertEqual(alpha_path.read_text(encoding="utf-8"), "new alpha")
        self.assertEqual(beta_path.read_text(encoding="utf-8"), "old beta")
        self.assertEqual(len(waits), 2)

    def test_stops_on_blocking_error_and_keeps_completed_update(self):
        alpha_path = self.create_account("alpha", "old alpha")
        beta_path = self.create_account("beta", "old beta")
        self.create_account("gamma", "old gamma")
        waits = []

        responses = {
            "alpha": SimpleNamespace(biography="new alpha"),
            "beta": instaloader.exceptions.ConnectionException(
                "401 Unauthorized"
            ),
        }

        def profile_response(_context, username):
            response = responses[username]
            if isinstance(response, Exception):
                raise response
            return response

        with patch.object(
            update_biography.instaloader.Profile,
            "from_username",
            side_effect=profile_response,
        ):
            result = update_biography.update_biography(
                self.root,
                loader=self.loader,
                sleep_fn=waits.append,
            )

        self.assertEqual(result.updated, ["alpha"])
        self.assertEqual(list(result.failed), ["beta"])
        self.assertEqual(result.skipped, ["gamma"])
        self.assertTrue(result.stopped_early)
        self.assertTrue(result.blocked)
        self.assertEqual(alpha_path.read_text(encoding="utf-8"), "new alpha")
        self.assertEqual(len(waits), 1)

    def test_ignores_non_account_directories(self):
        self.create_account("alpha", "old alpha")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_example.py").write_text(
            "pass\n",
            encoding="utf-8",
        )

        self.assertEqual(
            update_biography._get_subfolder_names(self.root),
            ["alpha"],
        )


if __name__ == "__main__":
    unittest.main()
