"""Command-line interface for the variant 5 assembler."""

import argparse
import sys
from pathlib import Path

from uvm.instructions import parse_program


def parse_arguments(arguments=None):
    """Read assembler command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Assembler for the variant 5 virtual machine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the source JSON program",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to the future binary output file",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Display intermediate instruction fields",
    )
    return parser.parse_args(arguments)


def load_instructions(path):
    """Read a JSON file and parse its instructions."""
    source = path.read_text(encoding="utf-8")
    return parse_program(source)


def print_instructions(program):
    """Display the fields of each parsed instruction."""
    for number, instruction in enumerate(program, start=1):
        print(
            f"{number}. {instruction.operation}: "
            f"A={instruction.a}, "
            f"B={instruction.b}, "
            f"C={instruction.c}"
        )


def main(arguments=None):
    """Run the first stage of the assembler."""
    config = parse_arguments(arguments)

    try:
        program = load_instructions(config.input)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Parsed instructions: {len(program)}")

    if config.test_mode:
        print_instructions(program)

    print(f"Binary target: {config.output}")
    print("Binary encoding will be added in stage 2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
