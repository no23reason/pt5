import math
import tkinter.filedialog
import turtle
from pathlib import Path
from tkinter import ttk

from pt5_core.ncp_model import NcpCommandType, NcpFile
from pt5_core.ncp_to_pt5 import ncp_to_pt5


def _safe_add(a: float, b: float) -> float:
    return round(a + b, 3)


class App:
    def __init__(self, master: tkinter.Tk):
        self.master = master
        self.master.title = "PT5"

        self.canvas_size = 800
        self.padding = 40

        self.source_filename = tkinter.StringVar()
        self.target_filename = tkinter.StringVar()
        self.should_animate = tkinter.BooleanVar()
        self.should_show_circle_centers = tkinter.BooleanVar()
        self.parsed: NcpFile | None = None

        frm = ttk.Frame(master, padding=10, width=800, height=1000)
        frm.grid()

        ttk.Label(frm, text="Source file").grid(column=0, row=0)
        ttk.Label(frm, textvariable=self.source_filename).grid(column=1, row=0, columnspan=3)

        ttk.Label(frm, text="Target file").grid(column=0, row=1)
        ttk.Label(frm, textvariable=self.target_filename).grid(column=1, row=1, columnspan=3)

        ttk.Checkbutton(frm, text="Animate", variable=self.should_animate).grid(column=0, row=2)
        ttk.Checkbutton(frm, text="Show circle centers", variable=self.should_show_circle_centers).grid(column=1, row=2)

        ttk.Button(frm, text="Select source file", command=self.open_ncp_file).grid(column=0, row=3)
        ttk.Button(frm, text="Convert", command=self.convert).grid(column=1, row=3)
        ttk.Button(frm, text="Draw", command=self.draw).grid(column=2, row=3)
        ttk.Button(frm, text="Quit", command=master.destroy).grid(column=3, row=3)

        self.canvas = tkinter.Canvas(self.master, height=self.canvas_size, width=self.canvas_size)
        self.canvas.grid(column=0, row=4, columnspan=4)

        self.turtle_screen = turtle.TurtleScreen(self.canvas)
        self.turtle = turtle.RawTurtle(self.turtle_screen, shape="blank")

    def open_ncp_file(self) -> None:
        source_filename = tkinter.filedialog.askopenfilename(filetypes=[("NCP files", "*.ncp")])
        target_filename = str(Path(source_filename).with_suffix(".pt5"))
        self.source_filename.set(source_filename)
        self.target_filename.set(target_filename)
        with open(self.source_filename.get()) as src:
            self.parsed = NcpFile.parse(src)

        self.draw()

    def convert(self) -> None:
        converted = ncp_to_pt5(self.parsed)
        with open(self.target_filename.get(), "w") as target:
            target.writelines(converted.serialize())

    def get_scaling(self) -> tuple[float, float, float]:
        """
        Return the tuple of scaling_factor, delta_x, delta_y so that the drawing fits the canvas neatly.
        This is a simple algorithm and may not work for not-so-well-behaved drawings: this is good enough for now.
        It works by collecting the extremes of both axes and the translating and scaling accordingly.
        """
        max_x = 0
        max_y = 0
        min_x = 0
        min_y = 0

        last_x = 0
        last_y = 0

        is_absolute = True

        for command in self.parsed.commands:
            if (
                command.type == NcpCommandType.MOVE
                or command.type == NcpCommandType.CLOCKWISE_CIRCLE
                or command.type == NcpCommandType.COUNTER_CLOCKWISE_CIRCLE
            ):
                if is_absolute:
                    new_x = command.arguments.get("X", last_x)
                    new_y = command.arguments.get("Y", last_y)
                else:
                    delta_x = command.arguments.get("X", 0)
                    delta_y = command.arguments.get("Y", 0)

                    new_x = _safe_add(last_x, delta_x)
                    new_y = _safe_add(last_y, delta_y)

                last_x = new_x
                last_y = new_y

                max_x = max(last_x, max_x)
                max_y = max(last_y, max_y)
                min_x = min(last_x, min_x)
                min_y = min(last_y, min_y)

            elif command.type == NcpCommandType.SET_INCREMENTAL_MODE:
                is_absolute = False
            elif command.type == NcpCommandType.SET_ABSOLUTE_MODE:
                is_absolute = True

        x_length = max_x - min_x
        y_length = max_y - min_y

        max_length = max(x_length, y_length)

        scaling = (self.canvas_size - 2 * self.padding) / max_length
        delta_x = x_length / 2
        delta_y = y_length / 2

        return scaling, delta_x, delta_y

    def draw(self) -> None:
        is_absolute = True

        # do the scaling manually, using world coordinates makes the turtle behave super weird and unpredictable
        scaling = self.get_scaling()

        def _scale_length(val: float) -> float:
            return val * scaling[0]

        def _scale_coordinates(coords: tuple[float, float]) -> tuple[float, float]:
            (x, y) = coords
            return (x + scaling[1]) * scaling[0], (y + scaling[2]) * scaling[0]

        def _descale_coordinates(coords: tuple[float, float]) -> tuple[float, float]:
            (x, y) = coords
            return x / scaling[0] - scaling[1], y / scaling[0] - scaling[2]

        self.turtle.reset()
        self.turtle.radians()

        if self.should_animate.get():
            self.turtle.speed(10)
        else:
            self.turtle.speed(0)

        # move the turtle to the scaled center first
        (scaled_x, scaled_y) = _scale_coordinates((0, 0))
        self.turtle.teleport(scaled_x, scaled_y)

        for command in self.parsed.commands:
            (last_x, last_y) = _descale_coordinates((self.turtle.xcor(), self.turtle.ycor()))

            if command.type == NcpCommandType.MOVE:
                if is_absolute:
                    new_x = command.arguments.get("X", last_x)
                    new_y = command.arguments.get("Y", last_y)

                    (scaled_x, scaled_y) = _scale_coordinates((new_x, new_y))
                    self.turtle.goto(scaled_x, scaled_y)
                # TODO relative
            elif (
                command.type == NcpCommandType.CLOCKWISE_CIRCLE
                or command.type == NcpCommandType.COUNTER_CLOCKWISE_CIRCLE
            ):
                if is_absolute:
                    new_x = command.arguments.get("X", last_x)
                    new_y = command.arguments.get("Y", last_y)

                    i = command.arguments.get("I", 0)
                    j = command.arguments.get("J", 0)

                    center_x = last_x + i
                    center_y = last_y + j

                    radius = math.hypot(i, j)
                    center_to_new = math.hypot(new_x - i - last_x, new_y - j - last_y)
                    last_to_new = math.hypot(new_x - last_x, new_y - last_y)

                    # use the law of cosines to figure out the angle of the arc
                    alpha = math.acos((radius**2 + center_to_new**2 - last_to_new**2) / (2 * radius * center_to_new))

                    # figure out the heading from the turtle to the center
                    heading_to_center = math.atan2(j, i)

                    # turn the turtle so that it has the center to its appropriate side
                    adjusted_heading = (
                        heading_to_center + math.pi / 2
                        if command.type == NcpCommandType.CLOCKWISE_CIRCLE
                        else heading_to_center - math.pi / 2
                    ) % math.tau

                    # set negative radius to make the turtle go clockwise if needed
                    if command.type == NcpCommandType.CLOCKWISE_CIRCLE:
                        radius = -radius

                    # now decide whether to use alpha or tau - alpha
                    # figure out the angles from center to start and end points
                    angle_from_center_to_start = math.atan2(last_y - center_y, last_x - center_x) % math.tau
                    angle_from_center_to_end = math.atan2(new_y - center_y, new_x - center_x) % math.tau

                    if command.type == NcpCommandType.CLOCKWISE_CIRCLE:
                        # if going the short way gets us to the target, use the short path
                        # for clockwise circles, the angle is decreasing, hence the minus alpha
                        if math.isclose((angle_from_center_to_start - alpha) % math.tau, angle_from_center_to_end):
                            extent = alpha
                        else:
                            extent = math.tau - alpha
                    else:
                        if math.isclose((angle_from_center_to_start + alpha) % math.tau, angle_from_center_to_end):
                            extent = alpha
                        else:
                            extent = math.tau - alpha

                    if self.should_show_circle_centers.get():
                        (scaled_x, scaled_y) = _scale_coordinates((center_x, center_y))
                        self.turtle.teleport(scaled_x, scaled_y)
                        self.turtle.dot(size=3)
                        (scaled_x, scaled_y) = _scale_coordinates((last_x, last_y))
                        self.turtle.teleport(scaled_x, scaled_y)

                    self.turtle.setheading(adjusted_heading)
                    self.turtle.circle(radius=_scale_length(radius), extent=extent)

                # TODO relative


root = tkinter.Tk()
app = App(root)
root.mainloop()
