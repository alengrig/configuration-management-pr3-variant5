"""Tests for parsing variant 5 machine instructions."""

import unittest
from pathlib import Path

from uvm.instructions import parse_instruction, parse_program


class InstructionTests(unittest.TestCase):
    """Check supported commands and invalid input."""

    def test_specification_program(self):
        """Match all four reference instruction fields."""
        root = Path(__file__).resolve().parents[1]
        path = root / "examples" / "specification.json"
        program = parse_program(path.read_text(encoding="utf-8"))

        actual = [
            (item.operation, item.a, item.b, item.c)
            for item in program
        ]
        expected = [
            ("load_const", 98, 7, 2),
            ("read_mem", 125, 0, 173),
            ("write_mem", 65, 2, 4),
            ("bit_not", 50, 716, 900),
        ]
        self.assertEqual(actual, expected)

    def test_valid_maximum_values(self):
        """Accept the largest allowed field values."""
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
                instruction = parse_instruction(record)
                self.assertEqual(instruction.b, record["b"])
                self.assertEqual(instruction.c, record["c"])

    def test_zero_values(self):
        """Accept zero in both operand fields."""
        record = {"op": "load_const", "b": 0, "c": 0}
        instruction = parse_instruction(record)
        self.assertEqual((instruction.b, instruction.c), (0, 0))

    def test_negative_values(self):
        """Reject negative operand values."""
        for field in ("b", "c"):
            with self.subTest(field=field):
                record = {"op": "load_const", "b": 7, "c": 2}
                record[field] = -1
                with self.assertRaises(ValueError):
                    parse_instruction(record)

    def test_overflow_values(self):
        """Reject values that exceed the bit width."""
        cases = [
            ("load_const", "b", 1 << 32),
            ("load_const", "c", 1 << 3),
            ("read_mem", "c", 1 << 13),
            ("write_mem", "b", 1 << 3),
            ("bit_not", "b", 1 << 13),
        ]

        for operation, field, value in cases:
            with self.subTest(operation=operation, field=field):
                record = {"op": operation, "b": 0, "c": 0}
                record[field] = value
                with self.assertRaises(ValueError):
                    parse_instruction(record)

    def test_boolean_values(self):
        """Reject booleans even though bool extends int."""
        for field in ("b", "c"):
            with self.subTest(field=field):
                record = {"op": "load_const", "b": 7, "c": 2}
                record[field] = True
                with self.assertRaises(ValueError):
                    parse_instruction(record)

    def test_float_values(self):
        """Reject floating-point operand values."""
        record = {"op": "load_const", "b": 7.5, "c": 2}
        with self.assertRaises(ValueError):
            parse_instruction(record)

    def test_missing_field(self):
        """Reject instructions with missing fields."""
        record = {"op": "load_const", "b": 7}
        with self.assertRaises(ValueError):
            parse_instruction(record)

    def test_extra_field(self):
        """Reject instructions with unexpected fields."""
        record = {"op": "load_const", "b": 7, "c": 2, "x": 1}
        with self.assertRaises(ValueError):
            parse_instruction(record)

    def test_unknown_operation(self):
        """Reject an unknown instruction name."""
        record = {"op": "unknown", "b": 0, "c": 0}
        with self.assertRaises(ValueError):
            parse_instruction(record)

    def test_invalid_record_type(self):
        """Reject a record that is not a dictionary."""
        with self.assertRaises(ValueError):
            parse_instruction(["load_const", 7, 2])

    def test_invalid_json(self):
        """Reject malformed JSON input."""
        with self.assertRaises(ValueError):
            parse_program('[{"op": "load_const",}]')

    def test_empty_program(self):
        """Reject an empty instruction list."""
        with self.assertRaises(ValueError):
            parse_program("[]")

    def test_invalid_program_root(self):
        """Require a JSON array as the program root."""
        with self.assertRaises(ValueError):
            parse_program('{"op": "load_const"}')

    def test_invalid_program_element(self):
        """Reject a non-object entry in a JSON program."""
        with self.assertRaises(ValueError):
            parse_program('[{"op": "load_const", "b": 7, "c": 2}, 5]')


if __name__ == "__main__":
    unittest.main()
