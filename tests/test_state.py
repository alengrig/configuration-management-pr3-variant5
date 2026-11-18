"""Tests for virtual machine registers and unified memory."""

import unittest

from uvm.state import MEMORY_SIZE, REGISTER_COUNT, MachineState

REFERENCE = bytes.fromhex(
    "62 07 00 00 00 02 "
    "7d 68 05 00 00 00 "
    "41 22 00 00 00 00 "
    "32 cc 82 70 00 00"
)


class MachineStateTests(unittest.TestCase):
    """Check binary loading and instruction fetching."""

    def setUp(self):
        """Create an empty virtual machine."""
        self.machine = MachineState()

    def test_initial_state(self):
        """Initialize memory, registers and program counter."""
        self.assertEqual(len(self.machine.memory), MEMORY_SIZE)
        self.assertEqual(len(self.machine.registers), REGISTER_COUNT)
        self.assertEqual(self.machine.registers, [0] * REGISTER_COUNT)
        self.assertEqual(self.machine.pc, 0)
        self.assertEqual(self.machine.program_size, 0)

    def test_load_binary(self):
        """Copy machine code into unified memory."""
        self.machine.load_program(REFERENCE)
        self.assertEqual(self.machine.program_size, 24)
        self.assertEqual(self.machine.memory[:24], REFERENCE)

    def test_fetch_first_instruction(self):
        """Read the first machine instruction."""
        self.machine.load_program(REFERENCE)
        instruction = self.machine.fetch_instruction()
        self.assertEqual(instruction.operation, "load_const")
        self.assertEqual((instruction.b, instruction.c), (7, 2))

    def test_fetch_second_instruction(self):
        """Read the instruction at the next byte address."""
        self.machine.load_program(REFERENCE)
        self.machine.pc = 6
        instruction = self.machine.fetch_instruction()
        self.assertEqual(instruction.operation, "read_mem")
        self.assertEqual((instruction.b, instruction.c), (0, 173))

    def test_unified_memory(self):
        """Fetch modified instructions from the same memory."""
        self.machine.load_program(REFERENCE)
        replacement = bytes.fromhex("41 22 00 00 00 00")
        self.machine.memory[:6] = replacement
        instruction = self.machine.fetch_instruction()
        self.assertEqual(instruction.operation, "write_mem")

    def test_reset_state(self):
        """Reset registers and memory when loading a new program."""
        self.machine.load_program(REFERENCE)
        self.machine.registers[0] = 123
        self.machine.memory[24] = 99
        self.machine.pc = 6
        self.machine.load_program(REFERENCE[:6])
        self.assertEqual(self.machine.registers[0], 0)
        self.assertEqual(self.machine.memory[24], 0)
        self.assertEqual(self.machine.pc, 0)

    def test_reject_empty_program(self):
        """Reject a binary file with no instructions."""
        with self.assertRaises(ValueError):
            self.machine.load_program(b"")

    def test_reject_wrong_type(self):
        """Require a bytes object as the binary program."""
        with self.assertRaises(ValueError):
            self.machine.load_program([98, 7, 0, 0, 0, 2])

    def test_reject_incomplete_program(self):
        """Reject a truncated machine instruction."""
        with self.assertRaises(ValueError):
            self.machine.load_program(b"\x62")

    def test_reject_oversized_program(self):
        """Reject programs that do not fit into memory."""
        size = (MEMORY_SIZE // 6 + 1) * 6
        with self.assertRaises(ValueError):
            self.machine.load_program(bytes(size))

    def test_fetch_without_program(self):
        """Reject instruction fetching before loading code."""
        with self.assertRaises(ValueError):
            self.machine.fetch_instruction()

    def test_invalid_program_counter(self):
        """Reject misaligned or out-of-range instruction addresses."""
        self.machine.load_program(REFERENCE)

        for address in (-6, 1, 24):
            with self.subTest(address=address):
                self.machine.pc = address
                with self.assertRaises(ValueError):
                    self.machine.fetch_instruction()


if __name__ == "__main__":
    unittest.main()
