"""Decode six-byte instructions of the variant 5 virtual machine."""

from uvm.encoding import INSTRUCTION_SIZE, encode_instruction
from uvm.instructions import OPERATIONS, Instruction

OPCODES = {
    opcode: (operation, b_width, c_width)
    for operation, (opcode, b_width, c_width) in OPERATIONS.items()
}


def decode_instruction(data):
    """Decode one machine instruction from six bytes."""
    if not isinstance(data, bytes):
        raise ValueError("Instruction must contain bytes")

    if len(data) != INSTRUCTION_SIZE:
        raise ValueError("Instruction must contain exactly six bytes")

    value = int.from_bytes(data, byteorder="little")
    opcode = value & 0xFF

    if opcode not in OPCODES:
        raise ValueError(f"Unknown opcode: {opcode}")

    operation, b_width, c_width = OPCODES[opcode]

    b = (value >> 8) & ((1 << b_width) - 1)
    c = (value >> (8 + b_width)) & ((1 << c_width) - 1)

    instruction = Instruction(operation, opcode, b, c)

    if encode_instruction(instruction) != data:
        raise ValueError("Instruction contains nonzero reserved bits")

    return instruction


def decode_program(data):
    """Decode a complete binary program."""
    if not isinstance(data, bytes):
        raise ValueError("Program must contain bytes")

    if not data or len(data) % INSTRUCTION_SIZE != 0:
        raise ValueError("Invalid binary program length")

    return [
        decode_instruction(data[index:index + INSTRUCTION_SIZE])
        for index in range(0, len(data), INSTRUCTION_SIZE)
    ]
