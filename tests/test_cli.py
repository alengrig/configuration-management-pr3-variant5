"""Tests for the assembler command-line interface."""

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from uvm.main import main, parse_arguments

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "specification.json"


class CommandLineTests(unittest.TestCase):
    """Check assembler startup and error handling."""

    def run_main(self, arguments):
        """Capture the program output and exit code."""
        stdout = StringIO()
        stderr = StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(arguments)

        return code, stdout.getvalue(), stderr.getvalue()

    def test_help(self):
        """Display CLI usage information."""
        output = StringIO()

        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                parse_arguments(["--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("--test-mode", output.getvalue())

    def test_required_arguments(self):
        """Reject a call without required paths."""
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as raised:
                parse_arguments([])

        self.assertEqual(raised.exception.code, 2)

    def test_test_mode(self):
        """Display all reference instructions."""
        arguments = [
            "--input", str(EXAMPLE),
            "--output", "output/specification.bin",
            "--test-mode",
        ]

        code, output, error = self.run_main(arguments)

        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertIn("Parsed instructions: 4", output)
        self.assertIn("load_const: A=98, B=7, C=2", output)
        self.assertIn("bit_not: A=50, B=716, C=900", output)
        self.assertIn("load_const: 62 07 00 00 00 02", output)
        self.assertIn("read_mem: 7d 68 05 00 00 00", output)
        self.assertIn("write_mem: 41 22 00 00 00 00", output)
        self.assertIn("bit_not: 32 cc 82 70 00 00", output)

    def test_normal_mode(self):
        """Parse instructions without verbose output."""
        with TemporaryDirectory() as folder:
            target = Path(folder) / "program.bin"
            arguments = [
                "--input", str(EXAMPLE),
                "--output", str(target),
            ]

            code, output, error = self.run_main(arguments)

            self.assertEqual(code, 0)
            self.assertEqual(error, "")
            self.assertIn("Parsed instructions: 4", output)
            self.assertNotIn("load_const:", output)
            self.assertEqual(target.stat().st_size, 24)

    def test_missing_input_file(self):
        """Report an input file that does not exist."""
        with TemporaryDirectory() as folder:
            missing = Path(folder) / "missing.json"
            arguments = [
                "--input", str(missing),
                "--output", str(Path(folder) / "out.bin"),
            ]

            code, output, error = self.run_main(arguments)

            self.assertEqual(code, 1)
            self.assertEqual(output, "")
            self.assertIn("Error:", error)

    def test_invalid_json_file(self):
        """Report malformed JSON without a traceback."""
        with TemporaryDirectory() as folder:
            source = Path(folder) / "invalid.json"
            source.write_text("{invalid", encoding="utf-8")
            arguments = [
                "--input", str(source),
                "--output", str(Path(folder) / "out.bin"),
            ]

            code, output, error = self.run_main(arguments)

            self.assertEqual(code, 1)
            self.assertEqual(output, "")
            self.assertIn("Invalid JSON", error)


if __name__ == "__main__":
    unittest.main()
