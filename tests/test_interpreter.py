"""Tests for the binary program interpreter."""

import unittest

from uvm.encoding import encode_program
from uvm.instructions import parse_instruction
from uvm.interpreter import run_program


def make_binary(records):
    """Assemble instruction records into binary code."""
    instructions = [parse_instruction(item) for item in records]
    return encode_program(instructions)


class InterpreterTests(unittest.TestCase):
    """Check complete binary program execution."""

    def test_load_constant(self):
        """Execute a binary constant-loading instruction."""
        binary = make_binary([
            {"op": "load_const", "b": 12345, "c": 3},
        ])
        machine = run_program(binary)

        self.assertEqual(machine.registers[3], 12345)
        self.assertEqual(machine.pc, 6)

    def test_memory_write_and_read(self):
        """Write a value and read it into another register."""
        records = [
            {"op": "load_const", "b": 123456789, "c": 0},
            {"op": "load_const", "b": 512, "c": 1},
            {"op": "write_mem", "b": 1, "c": 0},
            {"op": "read_mem", "b": 2, "c": 512},
        ]
        machine = run_program(make_binary(records))

        self.assertEqual(machine.read_word(512), 123456789)
        self.assertEqual(machine.registers[2], 123456789)
        self.assertEqual(machine.pc, 24)

    def test_copy_array(self):
        """Copy three values between memory regions."""
        values = [17, 256, 123456789]
        records = []

        for index, value in enumerate(values):
            address = 512 + index * 4
            records.extend([
                {"op": "load_const", "b": value, "c": 0},
                {"op": "load_const", "b": address, "c": 1},
                {"op": "write_mem", "b": 1, "c": 0},
            ])

        for index in range(len(values)):
            source = 512 + index * 4
            target = 1024 + index * 4
            records.extend([
                {"op": "read_mem", "b": 2, "c": source},
                {"op": "load_const", "b": target, "c": 3},
                {"op": "write_mem", "b": 3, "c": 2},
            ])

        machine = run_program(make_binary(records))
        result = [
            machine.read_word(1024 + index * 4)
            for index in range(len(values))
        ]

        self.assertEqual(result, values)

    def test_unified_memory(self):
        """Allow a program to modify its own instruction bytes."""
        records = [
            {"op": "load_const", "b": 0, "c": 1},
            {"op": "load_const", "b": 0x00002241, "c": 2},
            {"op": "write_mem", "b": 1, "c": 2},
        ]
        machine = run_program(make_binary(records))

        self.assertEqual(
            machine.memory[:4],
            bytes.fromhex("41 22 00 00"),
        )

    def test_invalid_binary_length(self):
        """Reject incomplete machine instructions."""
        with self.assertRaises(ValueError):
            run_program(b"\x62")

    def test_unknown_opcode(self):
        """Reject an unknown machine opcode."""
        with self.assertRaises(ValueError):
            run_program(bytes.fromhex("ff 00 00 00 00 00"))

    def test_unsupported_alu(self):
        """Reject ALU operations until stage four."""
        binary = make_binary([
            {"op": "bit_not", "b": 716, "c": 900},
        ])
        with self.assertRaises(ValueError):
            run_program(binary)


if __name__ == "__main__":
    unittest.main()
