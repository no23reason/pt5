import tkinter.filedialog
from pathlib import Path
from tkinter import ttk

from pt5_core.ncp_model import NcpFile
from pt5_core.ncp_to_pt5 import ncp_to_pt5


class App:
    def __init__(self, master: tkinter.Tk):
        self.master = master
        self.master.title = "PT5"

        self.source_filename = tkinter.StringVar()
        self.target_filename = tkinter.StringVar()

        frm = ttk.Frame(master, padding=10, width=800, height=600)
        frm.grid()

        ttk.Label(frm, text="Source file").grid(column=0, row=0)
        ttk.Label(frm, textvariable=self.source_filename).grid(column=1, row=0)

        ttk.Label(frm, text="Target file").grid(column=0, row=1)
        ttk.Label(frm, textvariable=self.target_filename).grid(column=1, row=1)

        ttk.Button(frm, text="Select source file", command=self.open_file).grid(column=0, row=2)
        ttk.Button(frm, text="Convert", command=self.convert).grid(column=1, row=2)
        ttk.Button(frm, text="Quit", command=master.destroy).grid(column=2, row=2)

    def open_file(self) -> None:
        source_filename = tkinter.filedialog.askopenfilename(filetypes=[("NCP files", "*.ncp")])
        target_filename = str(Path(source_filename).with_suffix(".pt5"))
        self.source_filename.set(source_filename)
        self.target_filename.set(target_filename)

    def convert(self) -> None:
        with open(self.source_filename.get()) as src:
            parsed = NcpFile.parse(src.readlines())
            converted = ncp_to_pt5(parsed)
            with open(self.target_filename.get(), "w") as target:
                target.writelines(converted.serialize())


root = tkinter.Tk()
app = App(root)
root.mainloop()
