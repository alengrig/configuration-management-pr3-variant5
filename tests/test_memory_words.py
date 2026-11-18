"""Tests for 32-bit values in unified machine memory."""

import unittest

from uvm.state import MachineState


class MemoryWordTests(unittest.TestCase):
    """Check reading and writing unsigned memory values."""

    def setUp(self):
        """Initialize an empty machine."""
        self.machine = MachineState()

    def test_zero_memory(self):
        """Read zero from a new memory area."""
        self.assertEqual(self.machine.read_word(512), 0)

    def test_word_round_trip(self):
        """Preserve a 32-bit value after writing and reading."""
        self.machine.write_word(512, 123456789)
        self.assertEqual(self.machine.read_word(512), 123456789)

    def test_little_endian(self):
        """Store bytes in little-endian order."""
        self.machine.write_word(512, 0x12345678)
        expected = bytes.fromhex("78 56 34 12")
        self.assertEqual(self.machine.memory[512:516], expected)

    def test_direct_byte_changes(self):
        """Read values directly modified in unified memory."""
        self.machine.memory[512:516] = bytes.fromhex(
            "ef cd ab 89"
        )
        self.assertEqual(self.machine.read_word(512), 0x89ABCDEF)

    def test_last_valid_address(self):
        """Allow the final complete four-byte memory word."""
        address = len(self.machine.memory) - 4
        self.machine.write_word(address, 0xFFFFFFFF)
        self.assertEqual(self.machine.read_word(address), 0xFFFFFFFF)

    def test_invalid_addresses(self):
        """Reject addresses that cannot hold four bytes."""
        invalid = (-1, True, 1.5, len(self.machine.memory) - 3)

        for address in invalid:
            with self.subTest(address=address):
                with self.assertRaises(ValueError):
                    self.machine.read_word(address)
                with self.assertRaises(ValueError):
                    self.machine.write_word(address, 1)

    def test_invalid_values(self):
        """Reject values outside the unsigned 32-bit range."""
        for value in (-1, 1 << 32, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.machine.write_word(512, value)

    def test_reset_memory(self):
        """Clear stored data when loading a new program."""
        self.machine.write_word(512, 98765)
        program = bytes.fromhex("62 07 00 00 00 02")
        self.machine.load_program(program)
        self.assertEqual(self.machine.read_word(512), 0)

    def test_shared_instruction_memory(self):
        """Use the same bytes for instructions and stored data."""
        program = bytes.fromhex("62 07 00 00 00 02")
        self.machine.load_program(program)

        self.machine.write_word(0, 0x00002241)

        self.assertEqual(
            self.machine.memory[:4],
            bytes.fromhex("41 22 00 00"),
        )


if __name__ == "__main__":
    unittest.main()
