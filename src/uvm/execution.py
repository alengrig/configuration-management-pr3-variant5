"""Execute basic instructions of the variant 5 virtual machine."""


def execute_instruction(machine, instruction):
    """Execute one basic instruction using registers and shared memory."""
    operation = instruction.operation

    if operation == "load_const":
        machine.registers[instruction.c] = instruction.b
    elif operation == "read_mem":
        value = machine.read_word(instruction.c)
        machine.registers[instruction.b] = value
    elif operation == "write_mem":
        address = machine.registers[instruction.b]
        value = machine.registers[instruction.c]
        machine.write_word(address, value)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
