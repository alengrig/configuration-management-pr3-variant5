"""Tests for binary file creation by the assembler."""

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from uvm.main import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "specification.json"

REFERENCE = bytes.fromhex(
    "62 07 00 00 00 02 "
    "7d 68 05 00 00 00 "
    "41 22 00 00 00 00 "
    "32 cc 82 70 00 00"
)


class BinaryCommandLineTests(unittest.TestCase):
    """Check output files and error handling."""

    def run_assembler(self, source, target):
        """Run the assembler and capture its messages."""
        output = StringIO()
        errors = StringIO()
        arguments = [
            "--input", str(source),
            "--output", str(target),
        ]

        with redirect_stdout(output), redirect_stderr(errors):
            code = main(arguments)

        return code, output.getvalue(), errors.getvalue()

    def test_binary_reference(self):
        """Create the exact reference binary file."""
        with TemporaryDirectory() as folder:
            target = Path(folder) / "program.bin"
            code, output, errors = self.run_assembler(EXAMPLE, target)

            self.assertEqual(code, 0)
            self.assertEqual(errors, "")
            self.assertIn("Binary size: 24 bytes", output)
            self.assertEqual(target.read_bytes(), REFERENCE)

    def test_nested_output_directory(self):
        """Create missing directories for the binary output."""
        with TemporaryDirectory() as folder:
            target = Path(folder) / "nested" / "program.bin"
            code, _, errors = self.run_assembler(EXAMPLE, target)

            self.assertEqual(code, 0)
            self.assertEqual(errors, "")
            self.assertEqual(target.stat().st_size, 24)

    def test_reject_overwriting_source(self):
        """Never overwrite the input JSON file."""
        with TemporaryDirectory() as folder:
            source = Path(folder) / "source.json"
            original = EXAMPLE.read_bytes()
            source.write_bytes(original)

            code, _, errors = self.run_assembler(source, source)

            self.assertEqual(code, 1)
            self.assertIn("Input and output paths must differ", errors)
            self.assertEqual(source.read_bytes(), original)

    def test_invalid_output_location(self):
        """Report an output path that is a directory."""
        with TemporaryDirectory() as folder:
            target = Path(folder) / "directory"
            target.mkdir()

            code, _, errors = self.run_assembler(EXAMPLE, target)

            self.assertEqual(code, 1)
            self.assertIn("Error:", errors)

    def test_invalid_json_does_not_create_binary(self):
        """Do not create output when input JSON is invalid."""
        with TemporaryDirectory() as folder:
            source = Path(folder) / "invalid.json"
            target = Path(folder) / "program.bin"
            source.write_text("{invalid", encoding="utf-8")

            code, _, errors = self.run_assembler(source, target)

            self.assertEqual(code, 1)
            self.assertIn("Invalid JSON", errors)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
