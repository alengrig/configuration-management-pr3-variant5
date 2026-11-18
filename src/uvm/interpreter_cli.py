"""Command-line interface for the binary UVM interpreter."""

import argparse
import sys
from pathlib import Path

from uvm.encoding import INSTRUCTION_SIZE
from uvm.interpreter import run_program
from uvm.xml_dump import write_memory_dump


def parse_arguments(arguments=None):
    """Parse interpreter command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a binary UVM program and export XML memory."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)

    return parser.parse_args(arguments)


def main(arguments=None):
    """Execute a binary program and save an XML memory dump."""
    config = parse_arguments(arguments)

    try:
        binary = config.input.read_bytes()
        machine = run_program(binary)
        path = write_memory_dump(
            machine, config.output, config.start, config.end
        )
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    count = machine.pc // INSTRUCTION_SIZE
    print(f"Executed instructions: {count}")
    print(f"XML memory dump: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
