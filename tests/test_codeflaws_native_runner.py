"""Resource failures must remain execution failures, not semantic counterexamples."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codeflaws_staged_study import bounded_process


@unittest.skipUnless(sys.platform.startswith("linux"), "POSIX resource limits")
class BoundedNativeProcessTests(unittest.TestCase):
    def run_control(self, command):
        # The production path executes already-compiled native programs.  Keep
        # these resource-limit controls independent of the invoking Python
        # environment: a large virtualenv can spend the entire one-second CPU
        # budget in interpreter startup before the control body is reached.
        with tempfile.TemporaryDirectory(prefix="repairseal-runner-control-") as directory:
            return bounded_process(["/bin/sh", "-c", command], b"", Path(directory))

    def test_output_cap_is_never_a_success(self):
        record, stdout, _stderr = self.run_control('printf "%05000d" 0')
        self.assertEqual(record["outcome"], "output_limit")
        self.assertEqual(len(stdout), 4096)
        self.assertGreater(record["stdout_bytes_seen"], 4096)
        self.assertTrue(record["truncated"])

    def test_timeout_is_never_a_success(self):
        record, _stdout, _stderr = self.run_control('sleep 5')
        self.assertEqual(record["outcome"], "timeout")

    def test_nonzero_exit_preserves_its_status(self):
        record, _stdout, _stderr = self.run_control('exit 7')
        self.assertEqual(record["outcome"], "nonzero")
        self.assertEqual(record["returncode"], 7)

    def test_regular_file_writes_are_bounded_at_zero(self):
        record, _stdout, _stderr = self.run_control('printf x > forbidden-payload')
        self.assertEqual(record["outcome"], "nonzero")


if __name__ == "__main__":
    unittest.main()
