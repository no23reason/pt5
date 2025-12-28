from pt5_core.ncp_model import NcpFile, NcpCommandType
from pt5_core.pt5_model import Pt5File, Pt5Command, Pt5CommandType


def _safe_add(a: float, b: float) -> float:
    return round(a + b, 3)


def _millimeters_to_micrometers(x: float) -> int:
    return round(x * 1000)


def ncp_to_pt5(model: NcpFile) -> Pt5File:
    is_absolute = True
    last_x = 0
    last_y = 0

    commands: list[Pt5Command] = []

    for command in model.commands:
        if command.type == NcpCommandType.MOVE:
            if is_absolute:
                new_x = command.arguments.get("X", last_x)
                new_y = command.arguments.get("Y", last_y)

                delta_x = _safe_add(new_x, -last_x)
                delta_y = _safe_add(new_y, -last_y)
            else:
                delta_x = command.arguments.get("X", 0)
                delta_y = command.arguments.get("Y", 0)

                new_x = _safe_add(last_x, delta_x)
                new_y = _safe_add(last_y, delta_y)

            arguments: dict[str, int] = {}
            if delta_x:
                arguments["X"] = _millimeters_to_micrometers(delta_x)
            if delta_y:
                arguments["Y"] = _millimeters_to_micrometers(delta_y)

            commands.append(Pt5Command(type=Pt5CommandType.MOVE, arguments=arguments))

            last_x = new_x
            last_y = new_y
        elif (
            command.type == NcpCommandType.CLOCKWISE_CIRCLE
            or command.type == NcpCommandType.COUNTER_CLOCKWISE_CIRCLE
        ):
            if is_absolute:
                new_x = command.arguments.get("X", last_x)
                new_y = command.arguments.get("Y", last_y)

                delta_x = _safe_add(new_x, -last_x)
                delta_y = _safe_add(new_y, -last_y)

                i = command.arguments.get("I", 0)
                j = command.arguments.get("J", 0)
            else:
                delta_x = command.arguments.get("X", 0)
                delta_y = command.arguments.get("Y", 0)

                new_x = _safe_add(last_x, delta_x)
                new_y = _safe_add(last_y, delta_y)

                delta_i = command.arguments.get("I", 0)
                delta_j = command.arguments.get("J", 0)

                i = _safe_add(last_x, delta_i)
                j = _safe_add(last_y, delta_j)

            arguments: dict[str, int] = {}
            if delta_x:
                arguments["X"] = _millimeters_to_micrometers(delta_x)
            if delta_y:
                arguments["Y"] = _millimeters_to_micrometers(delta_y)
            if i:
                arguments["I"] = _millimeters_to_micrometers(i)
            if j:
                arguments["J"] = _millimeters_to_micrometers(j)

            commands.append(
                Pt5Command(
                    type=Pt5CommandType.CLOCKWISE_CIRCLE
                    if command.type == NcpCommandType.CLOCKWISE_CIRCLE
                    else Pt5CommandType.COUNTER_CLOCKWISE_CIRCLE,
                    arguments=arguments,
                )
            )

            last_x = new_x
            last_y = new_y

        elif command.type == NcpCommandType.STOP:
            commands.append(Pt5Command(type=Pt5CommandType.STOP))
        elif command.type == NcpCommandType.END:
            commands.append(Pt5Command(type=Pt5CommandType.END))
        elif command.type == NcpCommandType.STOP_AND_REWIND:
            commands.append(Pt5Command(type=Pt5CommandType.STOP_AND_REWIND))
        elif command.type == NcpCommandType.SET_INCREMENTAL_MODE:
            is_absolute = False
        elif command.type == NcpCommandType.SET_ABSOLUTE_MODE:
            is_absolute = True
        else:
            # TODO error handling
            pass

    return Pt5File(commands=commands)
