"""Integration tests for copying a six-word memory array."""

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from uvm.encoding import encode_program
from uvm.instructions import parse_instruction
from uvm.interpreter import run_program
from uvm.interpreter_cli import main

VALUES = [17, 256, 65535, 123456789, 2882400001, 4294967295]
EXAMPLE = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "copy_array.json"
)


class CopyArrayTests(unittest.TestCase):
    """Check the complete six-element array-copy program."""

    def setUp(self):
        """Assemble the example program for each test."""
        records = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        commands = [parse_instruction(item) for item in records]
        self.binary = encode_program(commands)

    def test_program_size(self):
        """Encode thirty-six instructions into 216 bytes."""
        self.assertEqual(len(self.binary), 216)

    def test_source_array(self):
        """Preserve the original six values."""
        machine = run_program(self.binary)
        actual = [machine.read_word(512 + i * 4) for i in range(6)]
        self.assertEqual(actual, VALUES)

    def test_target_array(self):
        """Copy all six values to the destination addresses."""
        machine = run_program(self.binary)
        actual = [machine.read_word(1024 + i * 4) for i in range(6)]
        self.assertEqual(actual, VALUES)

    def test_program_counter(self):
        """Execute all thirty-six machine instructions."""
        machine = run_program(self.binary)
        self.assertEqual(machine.pc, 216)

    def test_cli_xml_output(self):
        """Export the copied array using the interpreter CLI."""
        with TemporaryDirectory() as directory:
            binary_path = Path(directory) / "copy.bin"
            xml_path = Path(directory) / "copy.xml"
            binary_path.write_bytes(self.binary)

            arguments = [
                "--input", str(binary_path),
                "--output", str(xml_path),
                "--start", "1024",
                "--end", "1048",
            ]
            with redirect_stdout(StringIO()):
                result = main(arguments)

            root = ET.parse(xml_path).getroot()
            actual = [int(item.text) for item in root.findall("word")]
            self.assertEqual(result, 0)
            self.assertEqual(actual, VALUES)


if __name__ == "__main__":
    unittest.main()
