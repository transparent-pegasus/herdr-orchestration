"""Execute the bootstrap's code block with a local mock, without a Herdr session."""

import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class HerdrGuideTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="herdr-guide-test-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.calls = self.directory / "calls"
        self.guide = "Synthetic test guide: first line.\nFinal line of the test guide."
        self.binary = self.directory / "herdr"
        self.binary.write_text(
            '#!/bin/sh\n'
            'printf "%s\\n" "$*" >> "$HERDR_GUIDE_TEST_CALLS"\n'
            'if test "${HERDR_GUIDE_TEST_EXIT:-0}" != 0; then\n'
            '  printf "%s\\n" "guide unavailable" >&2\n'
            '  exit "$HERDR_GUIDE_TEST_EXIT"\n'
            'fi\n'
            'printf "%s\\n" "$HERDR_GUIDE_TEST_OUTPUT"\n'
        )
        self.binary.chmod(0o755)
        self.env = dict(os.environ, PATH=self.temp.name,
                        HERDR_GUIDE_TEST_CALLS=str(self.calls),
                        HERDR_GUIDE_TEST_OUTPUT=self.guide,
                        HERDR_GUIDE_TEST_EXIT="0")
        self.env.pop("HERDR_ENV", None)
        skill = (ROOT / "skills/herdr/SKILL.md").read_text()
        blocks = re.findall(r"```bash\n(.*?)\n```", skill, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        self.bootstrap = blocks[0]

    def invoke(self):
        return subprocess.run(["/bin/bash", "-c", self.bootstrap], env=self.env,
                              capture_output=True, text=True, timeout=5)

    def test_outside_herdr_never_invokes_the_cli(self):
        for value in (None, "", "0"):
            with self.subTest(value=value):
                if value is None:
                    self.env.pop("HERDR_ENV", None)
                else:
                    self.env["HERDR_ENV"] = value
                result = self.invoke()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertFalse(self.calls.exists())

    def test_loads_the_complete_guide_from_the_installed_cli(self):
        self.env["HERDR_ENV"] = "1"
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.guide + "\n")
        self.assertEqual(self.calls.read_text(), "--skill\n")

    def test_unsupported_guide_stops_without_a_fallback(self):
        self.env.update(HERDR_ENV="1", HERDR_GUIDE_TEST_EXIT="2")
        result = self.invoke()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("guide unavailable", result.stderr)
        self.assertEqual(self.calls.read_text(), "--skill\n")

    def test_missing_cli_stops_without_a_fallback(self):
        self.env["HERDR_ENV"] = "1"
        self.binary.unlink()
        result = self.invoke()
        self.assertEqual(result.returncode, 127)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.calls.exists())


if __name__ == "__main__":
    unittest.main()
