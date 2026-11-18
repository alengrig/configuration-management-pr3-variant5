"""Save selected virtual-machine memory words as XML."""

from pathlib import Path
from xml.etree import ElementTree as ET

from uvm.state import WORD_SIZE


def validate_dump_range(machine, start, end):
    """Validate the requested half-open memory range."""
    if type(start) is not int or type(end) is not int:
        raise ValueError("Memory range must contain integer addresses")

    if not 0 <= start < end <= len(machine.memory):
        raise ValueError("Memory dump range is outside available memory")

    if start % WORD_SIZE or end % WORD_SIZE:
        raise ValueError("Memory dump range must be word-aligned")


def build_memory_tree(machine, start, end):
    """Build an XML tree containing selected memory values."""
    validate_dump_range(machine, start, end)

    root = ET.Element(
        "memory",
        start=str(start),
        end=str(end),
        word_size=str(WORD_SIZE),
    )

    for address in range(start, end, WORD_SIZE):
        word = ET.SubElement(root, "word", address=str(address))
        word.text = str(machine.read_word(address))

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    return tree


def write_memory_dump(machine, output, start, end):
    """Save an XML memory dump to the requested file."""
    tree = build_memory_tree(machine, start, end)

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    return path
