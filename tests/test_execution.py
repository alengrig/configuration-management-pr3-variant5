"""Tests for executing basic virtual machine instructions."""

import unittest

from uvm.encoding import encode_program
from uvm.execution import execute_instruction
from uvm.instructions import parse_instruction
from uvm.state import MachineState


def instruction(operation, b, c):
    """Create a validated machine instruction."""
    return parse_instruction({"op": operation, "b": b, "c": c})


class ExecutionTests(unittest.TestCase):
    """Check register operations and shared memory access."""

    def setUp(self):
        """Create an empty machine."""
        self.machine = MachineState()

    def test_load_const(self):
        """Load a constant into the selected register."""
        command = instruction("load_const", 123456789, 2)
        execute_instruction(self.machine, command)
        self.assertEqual(self.machine.registers[2], 123456789)

    def test_load_const_max(self):
        """Load the largest possible unsigned constant."""
        command = instruction("load_const", 0xFFFFFFFF, 7)
        execute_instruction(self.machine, command)
        self.assertEqual(self.machine.registers[7], 0xFFFFFFFF)

    def test_read_mem(self):
        """Read a 32-bit value into a register."""
        self.machine.write_word(512, 24680)
        command = instruction("read_mem", 3, 512)
        execute_instruction(self.machine, command)
        self.assertEqual(self.machine.registers[3], 24680)

    def test_write_mem(self):
        """Write a register value to its indirect address."""
        self.machine.registers[1] = 1024
        self.machine.registers[2] = 98765
        command = instruction("write_mem", 1, 2)
        execute_instruction(self.machine, command)
        self.assertEqual(self.machine.read_word(1024), 98765)

    def test_copy_word(self):
        """Copy a memory word using three basic instructions."""
        self.machine.write_word(512, 123456789)
        commands = [
            instruction("load_const", 1024, 1),
            instruction("read_mem", 0, 512),
            instruction("write_mem", 1, 0),
        ]
        for command in commands:
            execute_instruction(self.machine, command)

        self.assertEqual(self.machine.read_word(1024), 123456789)

    def test_binary_program(self):
        """Execute instructions decoded from a binary program."""
        commands = [
            instruction("load_const", 1024, 1),
            instruction("read_mem", 0, 512),
            instruction("write_mem", 1, 0),
        ]
        self.machine.load_program(encode_program(commands))
        self.machine.write_word(512, 0xDEADBEEF)

        while self.machine.pc < self.machine.program_size:
            command = self.machine.next_instruction()
            execute_instruction(self.machine, command)

        self.assertEqual(self.machine.read_word(1024), 0xDEADBEEF)
        self.assertEqual(self.machine.pc, 18)

    def test_unified_memory(self):
        """Allow a memory instruction to modify machine code."""
        command = instruction("load_const", 7, 0)
        self.machine.load_program(encode_program([command]))
        self.machine.registers[1] = 0
        self.machine.registers[2] = 0x00002241

        execute_instruction(
            self.machine,
            instruction("write_mem", 1, 2),
        )

        result = self.machine.fetch_instruction()
        self.assertEqual(result.operation, "write_mem")

    def test_invalid_write_address(self):
        """Reject a register address outside memory."""
        self.machine.registers[1] = 65535
        self.machine.registers[2] = 42

        with self.assertRaises(ValueError):
            execute_instruction(
                self.machine,
                instruction("write_mem", 1, 2),
            )

    def test_invalid_read_address(self):
        """Reject a read that extends beyond available memory."""
        self.machine.memory = bytearray(514)

        with self.assertRaises(ValueError):
            execute_instruction(
                self.machine,
                instruction("read_mem", 0, 512),
            )

    def test_alu_not_implemented(self):
        """Reserve the bitwise NOT operation for the next stage."""
        command = instruction("bit_not", 716, 900)

        with self.assertRaises(ValueError):
            execute_instruction(self.machine, command)


if __name__ == "__main__":
    unittest.main()
