#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xml.dom.minidom

import Tkinter as Tk
import tkFileDialog
import tkMessageBox

from linemap import LineMap
from linemap import Span
from lineinfo import LineInfo
from style import Style


class Application(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

        self.style = Style.load('data/style.xml')
        self.filename = 'data/'

    def load(self):
        filename = tkFileDialog.askopenfilename(
            initialdir=os.path.dirname(self.filename))
        if filename:
            info = LineInfo.load(filename)
            self.line_map.draw(info, self.style, Span(-1, 0, -1))

            self.filename = filename

    def createWidgets(self):
        menubar = Tk.Menu(tearoff=1)
        #
        # Menu bar
        #
        mn_file = Tk.Menu(menubar)
        mn_file.add_command(label="Open...", command=self.load)
        mn_file.add("separator")
        mn_file.add_command(label="Quit", command=self.quit)

        menubar.add_cascade(label="File", menu=mn_file, underline=0)
        self.master.configure(menu=menubar)

        self.line_map = LineMap(self)
        self.line_map.grid()

app = Application()
app.master.title("linemap")
app.mainloop()
