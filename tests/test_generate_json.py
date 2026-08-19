import json
import tempfile
import unittest
from pathlib import Path

from generate_json import generate_json


class GenerateJsonTests(unittest.TestCase):
    def test_uses_main_branch_for_generated_image_urls(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "sample_artist"
            profile.mkdir()
            (profile / "2026-08-15_12-00-00_UTC.jpg").write_bytes(b"image")
            (profile / "2026-08-15_12-00-00_UTC.txt").write_text(
                "Sample description", encoding="utf-8"
            )

            generate_json("example", "images", temp_dir)

            data = json.loads((root / "data.json").read_text(encoding="utf-8"))
            self.assertEqual(
                data["sample_artist"]["images"][0]["image"],
                "(https://raw.githubusercontent.com/example/images/main/"
                "sample_artist/2026-08-15_12-00-00_UTC.jpg)",
            )


if __name__ == "__main__":
    unittest.main()
