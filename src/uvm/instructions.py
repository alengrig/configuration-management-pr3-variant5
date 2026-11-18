"""Instruction definitions and validation for variant 5."""

import json
from dataclasses import dataclass

OPERATIONS = {
    "load_const": (98, 32, 3),
    "read_mem": (125, 3, 13),
    "write_mem": (65, 3, 3),
    "bit_not": (50, 13, 13),
}


@dataclass(frozen=True)
class Instruction:
    """Represent an instruction with fields A, B and C."""

    operation: str
    a: int
    b: int
    c: int


def validate_field(name, value, width):
    """Reject an integer outside the allowed bit width."""
    if type(value) is not int:
        raise ValueError(f"Field {name} must be an integer")

    if not 0 <= value < (1 << width):
        raise ValueError(f"Field {name} exceeds {width} bits")


def parse_instruction(record):
    """Convert a JSON object into a validated instruction."""
    if not isinstance(record, dict):
        raise ValueError("Instruction must be a JSON object")

    if set(record) != {"op", "b", "c"}:
        raise ValueError("Expected fields: op, b, c")

    operation = record["op"]

    if not isinstance(operation, str) or operation not in OPERATIONS:
        raise ValueError(f"Unknown operation: {operation}")

    opcode, b_width, c_width = OPERATIONS[operation]
    validate_field("B", record["b"], b_width)
    validate_field("C", record["c"], c_width)

    return Instruction(operation, opcode, record["b"], record["c"])


def parse_program(source):
    """Parse a JSON program into validated instructions."""
    try:
        records = json.loads(source)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON: {error}") from error

    if not isinstance(records, list) or not records:
        raise ValueError("Program must be a nonempty JSON array")

    return [parse_instruction(record) for record in records]
