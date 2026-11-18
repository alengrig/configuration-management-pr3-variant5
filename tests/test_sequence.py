"""Tests for sequential instruction fetching."""

import unittest

from uvm.state import MachineState

REFERENCE = bytes.fromhex(
    "62 07 00 00 00 02 "
    "7d 68 05 00 00 00 "
    "41 22 00 00 00 00 "
    "32 cc 82 70 00 00"
)


class SequenceTests(unittest.TestCase):
    """Check instruction fetching and program counter changes."""

    def setUp(self):
        """Load the reference binary program."""
        self.machine = MachineState()
        self.machine.load_program(REFERENCE)

    def test_first_instruction(self):
        """Read the first instruction and advance by six bytes."""
        instruction = self.machine.next_instruction()

        self.assertEqual(instruction.operation, "load_const")
        self.assertEqual(self.machine.pc, 6)

    def test_all_instructions(self):
        """Read the complete binary program in order."""
        operations = []

        while self.machine.pc < self.machine.program_size:
            instruction = self.machine.next_instruction()
            operations.append(instruction.operation)

        self.assertEqual(
            operations,
            ["load_const", "read_mem", "write_mem", "bit_not"],
        )
        self.assertEqual(self.machine.pc, 24)

    def test_end_of_program(self):
        """Reject reading beyond the last instruction."""
        self.machine.pc = self.machine.program_size

        with self.assertRaises(ValueError):
            self.machine.next_instruction()

    def test_invalid_counter(self):
        """Do not advance an invalid program counter."""
        self.machine.pc = 1

        with self.assertRaises(ValueError):
            self.machine.next_instruction()

        self.assertEqual(self.machine.pc, 1)

    def test_modified_instruction(self):
        """Read instructions from modified shared memory."""
        replacement = bytes.fromhex("41 22 00 00 00 00")
        self.machine.memory[:6] = replacement

        instruction = self.machine.next_instruction()

        self.assertEqual(instruction.operation, "write_mem")
        self.assertEqual(self.machine.pc, 6)


if __name__ == "__main__":
    unittest.main()
