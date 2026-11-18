"""Encode variant 5 instructions into six-byte machine code."""

from uvm.instructions import OPERATIONS, validate_field

INSTRUCTION_SIZE = 6
OPCODE_BITS = 8


def encode_instruction(instruction):
    """Encode one instruction using little-endian bit packing."""
    if instruction.operation not in OPERATIONS:
        raise ValueError("Unknown instruction operation")

    opcode, b_width, c_width = OPERATIONS[instruction.operation]

    if instruction.a != opcode:
        raise ValueError("Instruction opcode does not match operation")

    validate_field("B", instruction.b, b_width)
    validate_field("C", instruction.c, c_width)

    value = opcode
    value |= instruction.b << OPCODE_BITS
    value |= instruction.c << (OPCODE_BITS + b_width)

    return value.to_bytes(INSTRUCTION_SIZE, byteorder="little")


def encode_program(program):
    """Encode a sequence of instructions into machine code."""
    return b"".join(encode_instruction(item) for item in program)
