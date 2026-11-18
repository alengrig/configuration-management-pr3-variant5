"""Tests for six-byte instruction encoding."""

import unittest

from uvm.encoding import encode_instruction, encode_program
from uvm.instructions import Instruction, parse_instruction


class EncodingTests(unittest.TestCase):
    """Check encoding against the variant 5 specification."""

    def check_reference(self, operation, b, c, expected):
        """Compare encoded bytes with a reference sequence."""
        record = {"op": operation, "b": b, "c": c}
        instruction = parse_instruction(record)
        actual = encode_instruction(instruction)
        self.assertEqual(actual, bytes.fromhex(expected))
        self.assertEqual(len(actual), 6)

    def test_load_const_reference(self):
        """Match the constant-loading reference."""
        self.check_reference(
            "load_const", 7, 2, "62 07 00 00 00 02"
        )

    def test_read_mem_reference(self):
        """Match the memory-reading reference."""
        self.check_reference(
            "read_mem", 0, 173, "7d 68 05 00 00 00"
        )

    def test_write_mem_reference(self):
        """Match the memory-writing reference."""
        self.check_reference(
            "write_mem", 2, 4, "41 22 00 00 00 00"
        )

    def test_bit_not_reference(self):
        """Match the bitwise-NOT reference."""
        self.check_reference(
            "bit_not", 716, 900, "32 cc 82 70 00 00"
        )

    def test_complete_program(self):
        """Use six bytes per instruction in a complete program."""
        records = [
            ("load_const", 7, 2),
            ("read_mem", 0, 173),
            ("write_mem", 2, 4),
            ("bit_not", 716, 900),
        ]
        program = [
            parse_instruction({"op": op, "b": b, "c": c})
            for op, b, c in records
        ]
        result = encode_program(program)
        self.assertEqual(len(result), 24)

    def test_maximum_field_values(self):
        """Encode the largest supported values."""
        cases = [
            ("load_const", 32, 3),
            ("read_mem", 3, 13),
            ("write_mem", 3, 3),
            ("bit_not", 13, 13),
        ]
        for operation, b_width, c_width in cases:
            with self.subTest(operation=operation):
                record = {
                    "op": operation,
                    "b": (1 << b_width) - 1,
                    "c": (1 << c_width) - 1,
                }
                result = encode_instruction(parse_instruction(record))
                self.assertEqual(len(result), 6)

    def test_unknown_operation(self):
        """Reject an operation without a known opcode."""
        instruction = Instruction("unknown", 1, 0, 0)
        with self.assertRaises(ValueError):
            encode_instruction(instruction)

    def test_wrong_opcode(self):
        """Reject an opcode inconsistent with its operation."""
        instruction = Instruction("load_const", 1, 7, 2)
        with self.assertRaises(ValueError):
            encode_instruction(instruction)

    def test_invalid_operands(self):
        """Reject invalid operand values during encoding."""
        cases = [
            Instruction("load_const", 98, -1, 0),
            Instruction("load_const", 98, 0, 8),
            Instruction("read_mem", 125, 8, 0),
        ]
        for instruction in cases:
            with self.subTest(instruction=instruction):
                with self.assertRaises(ValueError):
                    encode_instruction(instruction)


if __name__ == "__main__":
    unittest.main()
