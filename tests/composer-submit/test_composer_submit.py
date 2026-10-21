"""Exercise the shipped helpers with a mock CLI and an ordinary local PTY.

No Herdr server, pane, or coding agent is started. The test process exposes its
own PTY so the helper's real /proc terminal-width checks run unchanged.
"""

import fcntl
import json
import os
from pathlib import Path
import pty
import shutil
import struct
import subprocess
import tempfile
import termios
import unittest


HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / "skills/using-herdr-sibling-panes/scripts"
INSTRUCTION = "Execute the scoped task in /repo/worktree. Write the report."


@unittest.skipUnless(Path("/proc/self/fd").exists(), "helpers measure Linux /proc terminals")
class ComposerSubmitTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="composer-submit-test-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.state_path = self.directory / "state.json"
        bin_dir = self.directory / "bin"
        bin_dir.mkdir()
        shutil.copyfile(HERE / "herdr_mock.py", bin_dir / "herdr")
        (bin_dir / "herdr").chmod(0o755)
        # Settle delays are unnecessary for the synchronous mock.
        (bin_dir / "sleep").write_text("#!/bin/sh\nexit 0\n")
        (bin_dir / "sleep").chmod(0o755)
        self.env = dict(os.environ, PATH=f'{bin_dir}:{os.environ["PATH"]}',
                        TMPDIR=self.temp.name, HERDR_SUBMIT_TEST_STATE=str(self.state_path),
                        HERDR_COMPOSER_INPUT_SETTLE_SECONDS="0",
                        HERDR_COMPOSER_CLEAR_SETTLE_SECONDS="0",
                        HERDR_COMPOSER_CONFIRM_TIMEOUT_SECONDS="2",
                        HERDR_COMPOSER_MIN_COLS="40")
        self.master, self.slave = pty.openpty()
        self.original_stdin = os.dup(0)
        os.dup2(self.slave, 0)
        self.addCleanup(self.close_terminal)
        self.configure()

    def close_terminal(self):
        os.dup2(self.original_stdin, 0)
        for fd in (self.original_stdin, self.master, self.slave):
            os.close(fd)

    def configure(self, **changes):
        state = dict(agent="cursor", status="idle", model="Muse Spark 1.3",
                     pid=os.getpid(), initial_cols=80, zoom_cols=100,
                     zoomed=False, zoom_pane="w1:p1", composer="",
                     resets=0, submissions=[], calls=[])
        state.update(changes)
        self.state_path.write_text(json.dumps(state))
        fcntl.ioctl(self.slave, termios.TIOCSWINSZ,
                    struct.pack("HHHH", 24, state["initial_cols"], 0, 0))

    def invoke(self, *args, script="composer-submit.sh", expected=0):
        result = subprocess.run(["bash", str(SCRIPTS / script), *args],
                                env=self.env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def state(self):
        return json.loads(self.state_path.read_text())

    def input_calls(self):
        return [call for call in self.state()["calls"]
                if call[:2] in (["pane", "send-text"], ["pane", "send-keys"])]

    def test_unpinned_submission_remains_compatible(self):
        self.invoke("w1:p2", INSTRUCTION)
        self.assertEqual(self.state()["resets"], 1)
        self.assertEqual(self.state()["submissions"], [INSTRUCTION])

    def test_model_pin_matches_case_insensitively_before_and_after_reset(self):
        self.invoke("w1:p2", INSTRUCTION, "muse spark 1.3")
        reads = [call for call in self.state()["calls"] if "visible" in call]
        self.assertEqual(len(reads), 2)
        self.assertEqual(self.state()["submissions"], [INSTRUCTION])

    def test_wrong_model_sends_no_input(self):
        self.invoke("w1:p2", INSTRUCTION, "Grok 4.7", expected=5)
        self.assertEqual(self.input_calls(), [])
        self.assertEqual(self.state()["resets"], 0)

    def test_unknown_model_rule_sends_no_input(self):
        self.configure(agent="unrecognized-cli")
        self.invoke("w1:p2", INSTRUCTION, "Muse Spark", expected=5)
        self.assertEqual(self.input_calls(), [])

    def test_model_change_after_reset_sends_no_instruction_and_restores_zoom(self):
        self.configure(initial_cols=24, model_after_reset="Grok 4.7")
        self.env["HERDR_COMPOSER_CONFIRM_TIMEOUT_SECONDS"] = "0"
        self.invoke("w1:p2", INSTRUCTION, "Muse Spark", expected=5)
        self.assertEqual(self.state()["resets"], 1)
        self.assertEqual(self.state()["submissions"], [])
        self.assertFalse(self.state()["zoomed"])

    def test_opencode_uses_new_session_keys(self):
        self.configure(agent="opencode", model="GPT-6.1 Sol")
        self.invoke("w1:p2", INSTRUCTION, "GPT-6.1 Sol")
        keys = [call[3] for call in self.input_calls() if call[1] == "send-keys"]
        self.assertEqual(keys[:2], ["ctrl+x", "n"])
        self.assertNotIn(["pane", "send-text", "w1:p2", "/clear"], self.input_calls())
        self.assertEqual(self.state()["resets"], 1)
        self.assertEqual(self.state()["submissions"], [INSTRUCTION])

    def test_empty_and_multiline_models_are_rejected(self):
        for model in ("", "Muse\nSpark"):
            with self.subTest(model=model):
                self.configure()
                self.invoke("w1:p2", INSTRUCTION, model, expected=2)
                self.assertEqual(self.input_calls(), [])

    def test_unsafe_instruction_is_rejected_before_input(self):
        for instruction in ("Execute\nanother line", "Execute the /run step"):
            with self.subTest(instruction=instruction):
                self.configure()
                self.invoke("w1:p2", instruction, expected=2)
                self.assertEqual(self.input_calls(), [])

    def test_working_and_blocked_panes_are_untouched(self):
        for status in ("working", "blocked"):
            with self.subTest(status=status):
                self.configure(status=status)
                self.invoke("w1:p2", INSTRUCTION, expected=2)
                self.assertEqual(self.input_calls(), [])

    def test_stale_agent_identity_at_shell_is_untouched(self):
        self.configure(shell_prompt=True)
        self.invoke("w1:p2", INSTRUCTION, expected=2)
        self.assertEqual(self.input_calls(), [])

    def test_too_narrow_pane_restores_zoom_without_input(self):
        self.configure(initial_cols=20, zoom_cols=30)
        self.invoke("w1:p2", INSTRUCTION, expected=4)
        self.assertFalse(self.state()["zoomed"])
        self.assertEqual(self.input_calls(), [])

    def test_existing_zoom_on_another_pane_is_restored(self):
        self.configure(initial_cols=20, zoomed=True, zoom_pane="w1:p3")
        self.invoke("w1:p2", INSTRUCTION)
        self.assertTrue(self.state()["zoomed"])
        self.assertEqual(self.state()["zoom_pane"], "w1:p3")
        self.assertEqual(self.state()["submissions"], [INSTRUCTION])

    def test_opencode_probe_checks_reset_wait_model_and_double_escape(self):
        self.configure(agent="opencode", model="GPT-6.1 Sol")
        result = self.invoke("w1:p2", "GPT-6.1 Sol", script="probe-composer.sh")
        self.assertEqual(result.stdout.count("PASS  "), 12, result.stdout)
        self.assertIn("9 esc esc interrupted", result.stdout)
        waits = [call for call in self.state()["calls"] if call[1] == "wait-output"]
        self.assertEqual(len(waits), 2)
        self.assertTrue(all("recent-unwrapped" in call for call in self.state()["calls"]
                            if call[:2] == ["pane", "read"] and "--lines" in call
                            and call[-1] == "60"))

    def test_probe_detects_reset_that_kept_the_conversation(self):
        self.configure(agent="opencode", model="GPT-6.1 Sol", ignore_resets=True)
        result = self.invoke("w1:p2", "GPT-6.1 Sol", script="probe-composer.sh", expected=1)
        self.assertIn("FAIL  8 the reset did not start a fresh conversation", result.stdout)


if __name__ == "__main__":
    unittest.main()
