"""Command-line interface for the variant 5 assembler."""

import argparse
import sys
from pathlib import Path

from uvm.encoding import encode_program
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
        help="Path to the binary output file",
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


def save_binary(program, source_path, output_path):
    """Encode and write a binary program."""
    if source_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must differ")

    binary = encode_program(program)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(binary)

    return len(binary)


def main(arguments=None):
    """Assemble JSON instructions into machine code."""
    config = parse_arguments(arguments)

    try:
        program = load_instructions(config.input)
        size = save_binary(program, config.input, config.output)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Parsed instructions: {len(program)}")

    if config.test_mode:
        print_instructions(program)

    print(f"Binary created: {config.output}")
    print(f"Binary size: {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
