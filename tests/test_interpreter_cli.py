"""Tests for the virtual machine interpreter CLI."""

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from uvm.encoding import encode_program
from uvm.instructions import parse_instruction
from uvm.interpreter_cli import main, parse_arguments


def make_binary(path):
    """Create a binary program that writes 42 to memory address 512."""
    records = [
        {"op": "load_const", "b": 42, "c": 0},
        {"op": "load_const", "b": 512, "c": 1},
        {"op": "write_mem", "b": 1, "c": 0},
    ]
    instructions = [parse_instruction(item) for item in records]
    path.write_bytes(encode_program(instructions))


class InterpreterCliTests(unittest.TestCase):
    """Check command-line parsing and XML output."""

    def test_parse_arguments(self):
        """Read paths and memory bounds from the command line."""
        arguments = [
            "--input", "program.bin",
            "--output", "memory.xml",
            "--start", "512",
            "--end", "520",
        ]
        config = parse_arguments(arguments)

        self.assertEqual(config.input, Path("program.bin"))
        self.assertEqual(config.output, Path("memory.xml"))
        self.assertEqual(config.start, 512)
        self.assertEqual(config.end, 520)

    def test_execute_and_export_xml(self):
        """Execute binary instructions and export actual memory."""
        with TemporaryDirectory() as directory:
            binary = Path(directory) / "program.bin"
            output = Path(directory) / "memory.xml"
            make_binary(binary)

            arguments = [
                "--input", str(binary),
                "--output", str(output),
                "--start", "512",
                "--end", "520",
            ]
            with redirect_stdout(StringIO()):
                result = main(arguments)

            self.assertEqual(result, 0)
            root = ET.parse(output).getroot()
            values = [int(item.text) for item in root.findall("word")]
            self.assertEqual(values, [42, 0])

    def test_create_output_directory(self):
        """Create missing directories for the XML dump."""
        with TemporaryDirectory() as directory:
            binary = Path(directory) / "program.bin"
            output = Path(directory) / "nested" / "memory.xml"
            make_binary(binary)

            arguments = [
                "--input", str(binary),
                "--output", str(output),
                "--start", "512",
                "--end", "516",
            ]
            with redirect_stdout(StringIO()):
                result = main(arguments)

            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())

    def test_missing_binary(self):
        """Report a missing binary file without creating XML."""
        with TemporaryDirectory() as directory:
            binary = Path(directory) / "missing.bin"
            output = Path(directory) / "memory.xml"
            arguments = [
                "--input", str(binary),
                "--output", str(output),
                "--start", "512",
                "--end", "516",
            ]
            with redirect_stderr(StringIO()):
                result = main(arguments)

            self.assertEqual(result, 1)
            self.assertFalse(output.exists())

    def test_invalid_binary(self):
        """Reject unknown machine instruction opcodes."""
        with TemporaryDirectory() as directory:
            binary = Path(directory) / "invalid.bin"
            output = Path(directory) / "memory.xml"
            binary.write_bytes(bytes.fromhex("ff 00 00 00 00 00"))

            arguments = [
                "--input", str(binary),
                "--output", str(output),
                "--start", "512",
                "--end", "516",
            ]
            with redirect_stderr(StringIO()):
                result = main(arguments)

            self.assertEqual(result, 1)
            self.assertFalse(output.exists())

    def test_invalid_memory_range(self):
        """Reject an unaligned XML memory range."""
        with TemporaryDirectory() as directory:
            binary = Path(directory) / "program.bin"
            output = Path(directory) / "memory.xml"
            make_binary(binary)

            arguments = [
                "--input", str(binary),
                "--output", str(output),
                "--start", "513",
                "--end", "520",
            ]
            with redirect_stderr(StringIO()):
                result = main(arguments)

            self.assertEqual(result, 1)
            self.assertFalse(output.exists())

    def test_missing_required_arguments(self):
        """Require all four command-line arguments."""
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as error:
                parse_arguments(["--input", "program.bin"])

        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
