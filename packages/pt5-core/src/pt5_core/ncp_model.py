from collections.abc import Iterable, Generator
from dataclasses import dataclass, field
from enum import StrEnum


class NcpCommandType(StrEnum):
    MOVE = "G01"
    CLOCKWISE_CIRCLE = "G02"
    COUNTER_CLOCKWISE_CIRCLE = "G03"
    SET_ABSOLUTE_MODE = "G90"
    SET_INCREMENTAL_MODE = "G91"
    STOP = "M00"
    END = "M02"
    STOP_AND_REWIND = "M30"


@dataclass
class NcpCommand:
    type: str  # NcpCommandType
    arguments: dict[str, float] = field(default_factory=dict)


@dataclass
class NcpFile:
    commands: list[NcpCommand] = field(default_factory=list)

    @staticmethod
    def parse(raw_lines: Iterable[str]) -> "NcpFile":
        return _parse_ncp(raw_lines)


def _parse_line(
    raw_line: str, current_command_type: str | None
) -> Generator[NcpCommand]:
    """
    Parse a single line of NCP.
    One line can have multiple commands.
    Also, some command types can span multiple lines so you don't have to repeat G01 over and over, for example::

        N001 G01 X1 Y2
        N002 G01 X2 Y3

    is the same as::

        N001 G01 X1 Y2
        N002 X2 Y3

    :param raw_line: the line to parse
    :param current_command_type: type of the currently "open" command from previous line
    :return: generator of commands on this line
    """
    parts = raw_line.rstrip("\n").split(" ")
    current_command: NcpCommand | None = None

    # drop the line number for now, no cross-referencing support
    if parts[0].startswith("N"):
        parts.pop(0)

    for part in parts:
        if part.startswith(("G", "M")):
            # new command, end the current one first
            if current_command:
                yield current_command
            current_command = NcpCommand(type=part)
            current_command_type = current_command.type
        else:
            # argument for an ongoing command, handle it
            if not current_command:
                # continue with the same command type as the previous line
                current_command = NcpCommand(type=current_command_type)
            current_command.arguments[part[0]] = float(part[1:])

    if current_command:
        yield current_command


def _parse_ncp(raw_lines: Iterable[str]) -> NcpFile:
    commands: list[NcpCommand] = []

    for raw_line in raw_lines:
        if raw_line.startswith("%"):
            # for now, ignore the comments
            continue

        if raw_line.startswith("N"):
            # numbered command
            commands.extend(
                _parse_line(
                    raw_line,
                    current_command_type=commands[-1].type if commands else None,
                )
            )

        # silently ignore unsupported line types

    return NcpFile(commands=commands)
