"""Tests for exporting virtual machine memory to XML."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from uvm.state import MachineState
from uvm.xml_dump import build_memory_tree, write_memory_dump


class XmlDumpTests(unittest.TestCase):
    """Check XML structure and memory address validation."""

    def setUp(self):
        """Initialize a machine with known values."""
        self.machine = MachineState()
        self.machine.write_word(512, 17)
        self.machine.write_word(516, 256)
        self.machine.write_word(520, 123456789)

    def test_root_attributes(self):
        """Preserve the requested range in XML attributes."""
        root = build_memory_tree(self.machine, 512, 524).getroot()

        self.assertEqual(root.tag, "memory")
        self.assertEqual(root.attrib["start"], "512")
        self.assertEqual(root.attrib["end"], "524")
        self.assertEqual(root.attrib["word_size"], "4")

    def test_memory_values(self):
        """Export all selected 32-bit values."""
        root = build_memory_tree(self.machine, 512, 524).getroot()
        values = [int(item.text) for item in root.findall("word")]

        self.assertEqual(values, [17, 256, 123456789])

    def test_memory_addresses(self):
        """Use byte addresses separated by four bytes."""
        root = build_memory_tree(self.machine, 512, 524).getroot()
        addresses = [
            int(item.attrib["address"])
            for item in root.findall("word")
        ]

        self.assertEqual(addresses, [512, 516, 520])

    def test_single_word(self):
        """Support a range containing exactly one value."""
        root = build_memory_tree(self.machine, 516, 520).getroot()
        words = root.findall("word")

        self.assertEqual(len(words), 1)
        self.assertEqual(words[0].text, "256")

    def test_write_xml_file(self):
        """Write a valid XML document with a declaration."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "memory.xml"
            write_memory_dump(self.machine, path, 512, 524)

            self.assertTrue(path.read_bytes().startswith(b"<?xml"))
            root = ET.parse(path).getroot()
            self.assertEqual(len(root.findall("word")), 3)

    def test_create_parent_directory(self):
        """Create missing directories for the output file."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "memory.xml"
            write_memory_dump(self.machine, path, 512, 516)

            self.assertTrue(path.is_file())

    def test_negative_start(self):
        """Reject a negative memory address."""
        with self.assertRaises(ValueError):
            build_memory_tree(self.machine, -4, 512)

    def test_empty_range(self):
        """Reject a range without memory words."""
        with self.assertRaises(ValueError):
            build_memory_tree(self.machine, 512, 512)

    def test_invalid_bounds(self):
        """Reject unaligned, oversized and boolean addresses."""
        invalid = [
            (513, 524),
            (512, 523),
            (512, 65540),
            (True, 524),
        ]

        for start, end in invalid:
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    build_memory_tree(self.machine, start, end)

    def test_invalid_range_does_not_create_file(self):
        """Do not create an XML file for an invalid range."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "memory.xml"

            with self.assertRaises(ValueError):
                write_memory_dump(self.machine, path, 513, 524)

            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
