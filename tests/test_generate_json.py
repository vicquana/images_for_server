import json
import tempfile
import unittest
from pathlib import Path

import generate_json


class GenerateJsonTests(unittest.TestCase):
    def test_writes_atomically_and_ignores_test_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            account = root / "alpha"
            account.mkdir()
            (account / "biography.txt").write_text("new bio", encoding="utf-8")

            test_fixture = root / "tests" / "fixture"
            test_fixture.mkdir(parents=True)
            (test_fixture / "example.jpg").write_bytes(b"not a real jpeg")

            generate_json.generate_json("owner", "repo", str(root))

            output = (root / "data.json").read_text(encoding="utf-8")
            payload = json.loads(output)

            self.assertEqual(list(payload), ["alpha"])
            self.assertEqual(payload["alpha"]["biography"], "new bio")
            self.assertTrue(output.endswith("\n"))
            self.assertEqual(list(root.glob(".data.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
