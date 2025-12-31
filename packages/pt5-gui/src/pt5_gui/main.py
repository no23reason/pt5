import math
import tkinter.filedialog
import turtle
from pathlib import Path
from tkinter import ttk

from pt5_core.ncp_model import NcpCommandType, NcpFile
from pt5_core.ncp_to_pt5 import ncp_to_pt5


class App:
    def __init__(self, master: tkinter.Tk):
        self.master = master
        self.master.title = "PT5"

        self.source_filename = tkinter.StringVar()
        self.target_filename = tkinter.StringVar()
        self.should_animate = tkinter.BooleanVar()
        self.should_show_circle_centers = tkinter.BooleanVar()
        self.parsed: NcpFile | None = None

        frm = ttk.Frame(master, padding=10, width=800, height=600)
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

        self.canvas = tkinter.Canvas(self.master, height=800, width=800)
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

    def draw(self) -> None:
        is_absolute = True

        # do the scaling manually, using world coordinates makes the turtle behave super weird and unpredictable
        scaling = 30

        self.turtle.reset()
        self.turtle.radians()

        if self.should_animate.get():
            self.turtle.speed(10)
        else:
            self.turtle.speed(0)

        for command in self.parsed.commands:
            last_x = self.turtle.xcor() / scaling
            last_y = self.turtle.ycor() / scaling

            if command.type == NcpCommandType.MOVE:
                if is_absolute:
                    new_x = command.arguments.get("X", last_x)
                    new_y = command.arguments.get("Y", last_y)

                    self.turtle.goto(new_x * scaling, new_y * scaling)
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
                        self.turtle.teleport(center_x * scaling, center_y * scaling)
                        self.turtle.dot(size=3)
                        self.turtle.teleport(last_x * scaling, last_y * scaling)

                    self.turtle.setheading(adjusted_heading)
                    self.turtle.circle(radius=radius * scaling, extent=extent)

                # TODO relative


root = tkinter.Tk()
app = App(root)
root.mainloop()
