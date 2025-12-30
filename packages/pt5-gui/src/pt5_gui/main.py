import math
import tkinter.filedialog
import turtle
from pathlib import Path
from tkinter import ttk

from pt5_core.ncp_model import NcpCommandType, NcpFile
from pt5_core.ncp_to_pt5 import ncp_to_pt5

_HALF_PI = math.pi / 2


class App:
    def __init__(self, master: tkinter.Tk):
        self.master = master
        self.master.title = "PT5"

        self.source_filename = tkinter.StringVar()
        self.target_filename = tkinter.StringVar()
        self.parsed: NcpFile | None = None

        frm = ttk.Frame(master, padding=10, width=800, height=600)
        frm.grid()

        ttk.Label(frm, text="Source file").grid(column=0, row=0)
        ttk.Label(frm, textvariable=self.source_filename).grid(column=1, row=0, columnspan=3)

        ttk.Label(frm, text="Target file").grid(column=0, row=1)
        ttk.Label(frm, textvariable=self.target_filename).grid(column=1, row=1, columnspan=3)

        ttk.Button(frm, text="Select source file", command=self.open_ncp_file).grid(column=0, row=2)
        ttk.Button(frm, text="Convert", command=self.convert).grid(column=1, row=2)
        ttk.Button(frm, text="Draw", command=self.draw).grid(column=2, row=2)
        ttk.Button(frm, text="Quit", command=master.destroy).grid(column=3, row=2)

        self.canvas = tkinter.Canvas(self.master, height=800, width=800)
        self.canvas.grid(row=3, columnspan=3)

        self.turtle_screen = turtle.TurtleScreen(self.canvas)
        self.turtle = turtle.RawTurtle(self.turtle_screen, shape="blank")

    def open_ncp_file(self) -> None:
        source_filename = tkinter.filedialog.askopenfilename(filetypes=[("NCP files", "*.ncp")])
        target_filename = str(Path(source_filename).with_suffix(".pt5"))
        self.source_filename.set(source_filename)
        self.target_filename.set(target_filename)
        with open(self.source_filename.get()) as src:
            self.parsed = NcpFile.parse(src)
        self.turtle.reset()

    def convert(self) -> None:
        converted = ncp_to_pt5(self.parsed)
        with open(self.target_filename.get(), "w") as target:
            target.writelines(converted.serialize())

    def draw(self) -> None:
        is_absolute = True

        self.turtle.reset()
        self.turtle.radians()
        self.turtle_screen.setworldcoordinates(-15, -15, 15, 15)

        for command in self.parsed.commands:
            last_x = self.turtle.xcor()
            last_y = self.turtle.ycor()

            if command.type == NcpCommandType.MOVE:
                if is_absolute:
                    new_x = command.arguments.get("X", last_x)
                    new_y = command.arguments.get("Y", last_y)

                    self.turtle.goto(new_x, new_y)
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
                    if i != 0:
                        heading_to_center = math.atan(j / i)
                    else:
                        if j < 0:
                            heading_to_center = 3 * _HALF_PI
                        else:
                            heading_to_center = _HALF_PI

                    # turn the turtle so that it has the center to its appropriate side
                    adjusted_heading = (
                        heading_to_center + _HALF_PI
                        if command.type == NcpCommandType.CLOCKWISE_CIRCLE
                        else heading_to_center - _HALF_PI
                    )

                    # set negative radius to make the turtle go clockwise if needed
                    if command.type == NcpCommandType.CLOCKWISE_CIRCLE:
                        radius = -radius

                    # now decide whether to use alpha or tau - alpha
                    # first, figure out the heading to the target
                    delta_x = new_x - last_x
                    delta_y = new_y - last_y

                    if delta_x != 0:
                        heading_to_target = math.atan(delta_y / delta_x)
                    else:
                        if delta_y < 0:
                            heading_to_target = 3 * _HALF_PI
                        else:
                            heading_to_target = _HALF_PI

                    if command.type == NcpCommandType.CLOCKWISE_CIRCLE:
                        if heading_to_center > heading_to_target:
                            extent = math.tau - alpha
                        else:
                            extent = alpha
                    else:
                        if heading_to_center > heading_to_target:
                            extent = alpha
                        else:
                            extent = math.tau - alpha

                    self.turtle.teleport(center_x, center_y)
                    self.turtle.dot()
                    self.turtle.teleport(last_x, last_y)

                    self.turtle.setheading(adjusted_heading)
                    self.turtle.circle(radius=radius, extent=extent, steps=math.ceil(extent * 20 / math.tau))

                # TODO relative


root = tkinter.Tk()
app = App(root)
root.mainloop()
