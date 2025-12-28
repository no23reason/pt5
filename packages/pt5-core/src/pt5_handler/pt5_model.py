from collections.abc import Generator
from dataclasses import dataclass, field
from enum import StrEnum


def _serialize_argument(name: str, micrometers: int) -> str:
    """
    Serialize the given argument.
    If the value is zero, nothing needs to be emitted.
    Any non-zero value must have a sign (even positive ones).
    :param name: the name of the argument
    :param micrometers: the value of the argument
    :return: serialized value
    """
    if micrometers == 0:
        return ""

    sign = "+" if micrometers > 0 else "-"
    return f"{name}{sign}{abs(micrometers) * 1000}"


class Pt5CommandType(StrEnum):
    MOVE = "G01"
    CLOCKWISE_CIRCLE = "G02"
    COUNTER_CLOCKWISE_CIRCLE = "G03"
    STOP = "M00"
    END = "M02"
    STOP_AND_REWIND = "M30"


@dataclass
class Pt5Command:
    type: Pt5CommandType
    arguments: dict[str, int] = field(default_factory=dict)


@dataclass
class Pt5File:
    commands: list[Pt5Command] = field(default_factory=list)

    def serialize(self) -> Generator[str]:
        return _serialize_pt5(self)


def _serialize_pt5(model: Pt5File) -> Generator[str]:
    line_number = 1
    last_line = ""

    for command in model.commands:
        if command.type == Pt5CommandType.MOVE:
            if last_line:
                yield last_line
            last_line = " ".join(
                filter(
                    None,
                    [
                        f"N{line_number}",
                        "G01",
                        _serialize_argument("X", command.arguments.get("X", 0)),
                        _serialize_argument("Y", command.arguments.get("Y", 0)),
                        # for some reason there needs to be M91 appended to the very first movement
                        "M91" if line_number == 1 else None,
                    ],
                ),
            )
            line_number += 1
        elif command.type == Pt5CommandType.CLOCKWISE_CIRCLE:
            if last_line:
                yield last_line
            last_line = " ".join(
                filter(
                    None,
                    [
                        f"N{line_number}",
                        "G02",
                        _serialize_argument("X", command.arguments.get("X", 0)),
                        _serialize_argument("Y", command.arguments.get("Y", 0)),
                        _serialize_argument("I", command.arguments.get("I", 0)),
                        _serialize_argument("J", command.arguments.get("J", 0)),
                        # for some reason there needs to be M91 appended to the very first movement
                        "M91" if line_number == 1 else None,
                    ],
                ),
            )
            line_number += 1
        elif command.type == Pt5CommandType.COUNTER_CLOCKWISE_CIRCLE:
            if last_line:
                yield last_line
            last_line = " ".join(
                filter(
                    None,
                    [
                        f"N{line_number}",
                        "G03",
                        _serialize_argument("X", command.arguments.get("X", 0)),
                        _serialize_argument("Y", command.arguments.get("Y", 0)),
                        _serialize_argument("I", command.arguments.get("I", 0)),
                        _serialize_argument("J", command.arguments.get("J", 0)),
                        # for some reason there needs to be M91 appended to the very first movement
                        "M91" if line_number == 1 else None,
                    ],
                ),
            )
            line_number += 1
        elif command.type == Pt5CommandType.END:
            last_line += " " + Pt5CommandType.END
        elif command.type == Pt5CommandType.STOP:
            last_line += " " + Pt5CommandType.STOP
        elif command.type == Pt5CommandType.STOP_AND_REWIND:
            last_line += " " + Pt5CommandType.STOP_AND_REWIND

    if last_line:
        yield last_line
