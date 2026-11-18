"""Tests for decoding variant 5 machine instructions."""

import unittest

from uvm.decoding import decode_instruction, decode_program
from uvm.encoding import encode_instruction, encode_program
from uvm.instructions import parse_instruction

REFERENCE = bytes.fromhex(
    "62 07 00 00 00 02 "
    "7d 68 05 00 00 00 "
    "41 22 00 00 00 00 "
    "32 cc 82 70 00 00"
)


class DecodingTests(unittest.TestCase):
    """Check decoding and invalid binary input."""

    def test_reference_instructions(self):
        """Recover all four reference instructions."""
        expected = [
            ("load_const", 98, 7, 2),
            ("read_mem", 125, 0, 173),
            ("write_mem", 65, 2, 4),
            ("bit_not", 50, 716, 900),
        ]

        program = decode_program(REFERENCE)
        actual = [
            (item.operation, item.a, item.b, item.c)
            for item in program
        ]

        self.assertEqual(actual, expected)

    def test_program_round_trip(self):
        """Re-encoding a decoded program preserves all bytes."""
        program = decode_program(REFERENCE)
        self.assertEqual(encode_program(program), REFERENCE)

    def test_instruction_round_trip(self):
        """Restore instructions with maximum operand values."""
        cases = [
            ("load_const", (1 << 32) - 1, 7),
            ("read_mem", 7, (1 << 13) - 1),
            ("write_mem", 7, 7),
            ("bit_not", (1 << 13) - 1, (1 << 13) - 1),
        ]

        for operation, b, c in cases:
            with self.subTest(operation=operation):
                record = {"op": operation, "b": b, "c": c}
                original = parse_instruction(record)
                restored = decode_instruction(
                    encode_instruction(original)
                )
                self.assertEqual(restored, original)

    def test_invalid_instruction_length(self):
        """Reject instructions shorter than six bytes."""
        with self.assertRaises(ValueError):
            decode_instruction(b"\x62\x07")

    def test_invalid_instruction_type(self):
        """Reject input that is not bytes."""
        with self.assertRaises(ValueError):
            decode_instruction("62 07 00 00 00 02")

    def test_unknown_opcode(self):
        """Reject an unknown machine instruction."""
        with self.assertRaises(ValueError):
            decode_instruction(b"\xff\x00\x00\x00\x00\x00")

    def test_reserved_bits(self):
        """Reject nonzero bits outside instruction fields."""
        data = bytes.fromhex("62 07 00 00 00 82")
        with self.assertRaises(ValueError):
            decode_instruction(data)

    def test_empty_program(self):
        """Reject an empty binary program."""
        with self.assertRaises(ValueError):
            decode_program(b"")

    def test_incomplete_program(self):
        """Reject a program with an incomplete final instruction."""
        with self.assertRaises(ValueError):
            decode_program(REFERENCE + b"\x00")

    def test_invalid_program_type(self):
        """Reject input that is not a byte sequence."""
        with self.assertRaises(ValueError):
            decode_program([98, 7, 0, 0, 0, 2])


if __name__ == "__main__":
    unittest.main()
