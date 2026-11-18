"""Run binary programs on the variant 5 virtual machine."""

from uvm.execution import execute_instruction
from uvm.state import MachineState


def run_program(binary):
    """Load and execute all instructions from a binary program."""
    machine = MachineState()
    machine.load_program(binary)

    while machine.pc < machine.program_size:
        instruction = machine.next_instruction()
        execute_instruction(machine, instruction)

    return machine
