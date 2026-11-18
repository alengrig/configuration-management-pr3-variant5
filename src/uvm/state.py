"""Store registers and unified memory of the virtual machine."""

from dataclasses import dataclass, field

from uvm.decoding import decode_instruction
from uvm.encoding import INSTRUCTION_SIZE

MEMORY_SIZE = 65536
REGISTER_COUNT = 8
WORD_SIZE = 4
MAX_WORD = (1 << 32) - 1


@dataclass
class MachineState:
    """Represent a virtual machine with one shared memory."""

    memory: bytearray = field(
        default_factory=lambda: bytearray(MEMORY_SIZE)
    )
    registers: list[int] = field(
        default_factory=lambda: [0] * REGISTER_COUNT
    )
    pc: int = 0
    program_size: int = 0

    def load_program(self, program):
        """Load binary code into shared memory and reset the state."""
        if not isinstance(program, bytes):
            raise ValueError("Program must contain bytes")

        if not program or len(program) % INSTRUCTION_SIZE:
            raise ValueError("Invalid binary program length")

        if len(program) > len(self.memory):
            raise ValueError("Program exceeds available memory")

        self.memory[:] = b"\x00" * len(self.memory)
        self.memory[:len(program)] = program
        self.registers[:] = [0] * REGISTER_COUNT
        self.pc = 0
        self.program_size = len(program)

    def validate_word_address(self, address):
        """Check a four-byte memory address."""
        if type(address) is not int:
            raise ValueError("Memory address must be an integer")

        if address < 0 or address + WORD_SIZE > len(self.memory):
            raise ValueError("Memory address is outside available memory")

    def read_word(self, address):
        """Read an unsigned 32-bit value from shared memory."""
        self.validate_word_address(address)
        data = self.memory[address:address + WORD_SIZE]
        return int.from_bytes(data, byteorder="little")

    def write_word(self, address, value):
        """Write an unsigned 32-bit value to shared memory."""
        self.validate_word_address(address)

        if type(value) is not int or not 0 <= value <= MAX_WORD:
            raise ValueError("Value must be an unsigned 32-bit integer")

        data = value.to_bytes(WORD_SIZE, byteorder="little")
        self.memory[address:address + WORD_SIZE] = data

    def fetch_instruction(self):
        """Read an instruction from shared memory at the current PC."""
        if self.pc % INSTRUCTION_SIZE:
            raise ValueError("Program counter is not aligned")

        if not 0 <= self.pc < self.program_size:
            raise ValueError("Program counter is outside the program")

        end = self.pc + INSTRUCTION_SIZE
        data = bytes(self.memory[self.pc:end])
        return decode_instruction(data)

    def next_instruction(self):
        """Read one instruction and advance the counter."""
        instruction = self.fetch_instruction()
        self.pc += INSTRUCTION_SIZE
        return instruction
