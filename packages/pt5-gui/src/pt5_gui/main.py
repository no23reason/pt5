import tkinter.filedialog
from tkinter import *
from tkinter import ttk
from pt5_core.ncp_model import NcpFile
from pt5_core.ncp_to_pt5 import ncp_to_pt5

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()


def open_file() -> None:
    file = tkinter.filedialog.askopenfile(mode="r", filetypes=[("NCP files", "*.ncp")])
    if file:
        lines = file.readlines()
        parsed = NcpFile.parse(lines)
        print("PARSED", parsed)
        converted = ncp_to_pt5(parsed)
        print("CONVERTED", converted)


ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Button(frm, text="Open", command=open_file).grid(column=1, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=2, row=0)

root.mainloop()
