import tkinter as tk
import serial


class dotEditor(tk.Frame):
    def __init__(self, rows, cols, scale=30, origin="TL"):
        if rows * cols > 4096:
            print("They make displays this big? Know where I can purchase one?...")
        self.root = tk.Tk()
        self.root.title("Flip-dot Design Canvas 2.0")
        self.numRows = int(rows)
        self.numCols = int(cols)
        self.scale = int(scale)
        self.origin = origin
        super().__init__(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.serialSyncActive = False
        self.previousCellNum = (-1,)
        self.previousCellFill = None
        self.serialConnection = None

        gridFrame = tk.Frame(self.root, bd=2, bg="gray")
        tk.Button(gridFrame, text="All On", command=lambda: self.allToggle('yellow')).grid(row=0, column=0)
        tk.Button(gridFrame, text="All Off", command=lambda: self.allToggle('black')).grid(row=0, column=1)
        tk.Button(gridFrame, text="Import", command=self.importArray).grid(row=0, column=2)
        tk.Button(gridFrame, text="Export", command=self.export).grid(row=0, column=3)
        self.imexBox = tk.StringVar(self.root)
        tk.Entry(gridFrame, textvariable=self.imexBox, width=30, fg="black").grid(row=0, column=4)

        tk.Label(gridFrame, text="Serial: ", width=8, justify="right").grid(row=0, column=5)
        self.comPort = tk.StringVar(self.root)
        tk.Entry(gridFrame, textvariable=self.comPort, width=8, fg="black").grid(row=0, column=6)
        self.comPort.set("COM_")
        self.baudRate = tk.IntVar(self.root)
        tk.Entry(gridFrame, textvariable=self.baudRate, width=8, fg="black").grid(row=0, column=7)
        self.baudRate.set(115200)
        self.scButton = tk.Button(gridFrame, text="Connect", command=self.serialConnect, relief="raised")
        self.scButton.grid(row=0, column=8)
        tk.Button(gridFrame, text="Export", command=self.serialExport).grid(row=0, column=9)
        self.tssButton = tk.Button(gridFrame, text="Sync", command=self.toggleSerialSync, relief="raised")
        self.tssButton.grid(row=0, column=10)
        gridFrame.pack()

        self.canvas = tk.Canvas(self.root, width=self.numCols * scale, height=self.numRows * scale)
        self.canvas.pack(fill="both", expand=True)

        for row in range(self.numRows):
            for column in range(self.numCols):
                x0, y0 = (column * scale), (row * scale)
                x1, y1 = (x0 + scale), (y0 + scale)
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="black", outline="gray",
                                             tags=(self.tag(row, column), "cell"))
        self.canvas.tag_bind("cell", "<B1-Motion>", lambda event: self.paint(event, "yellow"))
        self.canvas.tag_bind("cell", "<Button-1>", lambda event: self.paint(event, "yellow"))
        self.canvas.tag_bind("cell", "<B3-Motion>", lambda event: self.paint(event, "black"))
        self.canvas.tag_bind("cell", "<Button-3>", lambda event: self.paint(event, "black"))
        self.root.mainloop()

    def tag(self, row, column):
        tag = f"{row},{column}"
        return tag

    def export(self):
        output = []
        if self.origin == "TL":
            for column in range(self.numCols):
                output.append(0)
                for row in range(self.numRows):
                    if self.canvas.itemcget(self.tag(row, column), "fill") == "yellow":
                        output[column] += 2 ** row
        elif self.origin == "BL":
            for column in range(self.numCols):
                output.append(0)
                for row in range(self.numRows):
                    if self.canvas.itemcget(self.tag(row, column), "fill") == "yellow":
                        output[column] += 2 ** (self.numRows - row - 1)
        formatted = f'{{{",".join([str(x) for x in output])}}};\n'
        self.imexBox.set(formatted)
        print(formatted, end="")
        return formatted

    def importArray(self):
        array = self.imexBox.get()
        array = array[array.index('{')+1:array.index('}')].split(",")
        if self.origin == "TL":
            for column in range(min(len(array), self.numCols)):
                for row in range(self.numRows):
                    if (int(array[column]) >> row) & 1:
                        self.canvas.itemconfig(self.tag(row, column), fill="yellow")
        elif self.origin == "BL":
            for column in range(min(len(array), self.numCols)):
                for row in range(self.numRows):
                    if (int(array[column]) >> (self.numRows - row - 1)) & 1:
                        self.canvas.itemconfig(self.tag(row, column), fill="yellow")
        if self.serialSyncActive:
            self.serialExport()

    def allToggle(self, fill):
        for column in range(self.numCols):
            for row in range(self.numRows):
                self.canvas.itemconfig(self.tag(row, column), fill=fill)
        if self.serialSyncActive:
            self.serialExport()

    def paint(self, event, fill):
        cell = self.canvas.find_closest(event.x, event.y)
        self.canvas.itemconfigure(cell, fill=fill)
        if self.serialSyncActive and (self.previousCellNum != cell[0] or self.previousCellFill != fill):
            self.previousCellFill = fill
            self.previousCellNum = cell[0]
            if fill == "yellow":
                self.serialConnection.write(f'({self.canvas.itemcget(cell, "tags").split(" ")[0]},1)\n'.encode('ascii','ignore'))
            else:
                self.serialConnection.write(f'({self.canvas.itemcget(cell, "tags").split(" ")[0]},0)\n'.encode('ascii','ignore'))


    def serialConnect(self):
        if self.serialConnection is None and self.comPort.get() != "COM_":
            try:
                self.serialConnection = serial.Serial(self.comPort.get(), self.baudRate.get())
                self.scButton.config(relief="sunken")
                print("Connected to serial port.")
            except:
                print("Could not connect to serial port.")
                self.serialConnection = None
        elif self.serialConnection is not None and self.serialConnection.is_open:
            self.serialConnection.close()
            self.serialConnection = None
            self.scButton.config(relief="raised")
            print("Disconnected from serial port.")
        elif self.comPort.get() == "COM_":
            print("No serial port selected.")
        else:
            self.serialConnection = None
            self.scButton.config(relief="raised")

    def serialExport(self):
        if self.serialConnection is not None:
            if self.serialConnection.is_open:
                self.serialConnection.write(self.export().encode('ascii','ignore'))
        else:
            print("No serial connection established.")

    def toggleSerialSync(self):
        if not self.serialSyncActive and self.serialConnection is not None and self.serialConnection.is_open:
            self.serialSyncActive = True
            self.tssButton.config(relief="sunken")
            self.serialExport()
        elif self.serialConnection is None or not self.serialConnection.is_open:
            print("No serial connection established.")
        else:
            self.serialSyncActive = False
            self.tssButton.config(relief="raised")

    def on_closing(self):
        if self.serialConnection is not None and self.serialConnection.is_open:
            self.serialConnection.close()
        self.root.destroy()
        menu()



class menu:
    def __init__(self):
        menu = tk.Tk()
        windowWidth = 250
        windowHeight = 335
        menu.geometry(str(windowWidth) + "x" + str(windowHeight))
        menu.title("Flip-dot Designer Menu")

        tk.Label(menu, height=1, text="Flip-dot Designer", anchor="n", justify="center", font=("Helvetica", 20)).grid(row=0, column=0, rowspan=2, columnspan=2)

        numRows = tk.IntVar()
        tk.Label(menu, text='Number Of Rows:        ', anchor="w", justify="left").grid(row=2, column=0)
        tk.Entry(menu, textvariable=numRows, width=16, justify="right").grid(row=2, column=1)
        numRows.set(16)

        numCols = tk.IntVar()
        tk.Label(menu, text='Number Of Columns:  ', anchor="w", justify="left").grid(row=3, column=0)
        tk.Entry(menu, textvariable=numCols, width=16, justify="right").grid(row=3, column=1)
        numCols.set(112)

        scale = tk.IntVar()
        tk.Label(menu, text='Dot Scale:                      ', anchor="w", justify="left").grid(row=4, column=0)
        tk.Entry(menu, textvariable=scale, width=16, justify="right").grid(row=4, column=1)
        scale.set(18)

        tk.Label(menu, text='Origin:                           ', anchor="w", justify="left").grid(row=5, column=0)
        self.originButton = tk.Button(menu, text="Top Left", width=16, justify="right", command=self.changeOrigin)
        self.originButton.grid(row=5, column=1)
        self.origin = "TL"

        tk.Button(menu, width=16, height=1, text="Launch", bg='grey',
                  command=lambda: [menu.destroy(), dotEditor(numRows.get(), numCols.get(), scale.get(), self.origin)]).grid(row=6, column=1)

        tk.Label(menu, height=1).grid(row=7, column=0)

        tk.Label(menu, height=1, text="Quick Buttons:", anchor="w", justify="left").grid(row=8, column=0)

        self.quickButtons = []
        self.quickButtons.append(tk.Button(menu, width=16, height=1, text="16R x 112C (18s) TL", bg='grey',
                                 command=lambda: [menu.destroy(), dotEditor(16, 112, 18, self.origin)]))
        self.quickButtons[-1].grid(row=9, column=0)

        self.quickButtons.append(tk.Button(menu, width=16, height=1, text="16R x 28C (40s) TL", bg='grey',
                                           command=lambda: [menu.destroy(), dotEditor(16, 28, 40, self.origin)]))
        self.quickButtons[-1].grid(row=9, column=1)

        self.quickButtons.append(tk.Button(menu, width=16, height=1, text="8R x 8C (85s) TL", bg='grey',
                                           command=lambda: [menu.destroy(), dotEditor(8, 8, 85, self.origin)]))
        self.quickButtons[-1].grid(row=10, column=0)

        self.quickButtons.append(tk.Button(menu, width=16, height=1, text="7R x 90C (22s) TL", bg='grey',
                                 command=lambda: [menu.destroy(), dotEditor(7, 90, 22, self.origin)]))
        self.quickButtons[-1].grid(row=10, column=1)

        tk.Label(menu, height=1).grid(row=11)

        tk.Label(menu, text='Flip-dot Designer    Version 2.0\nProgrammed by:   Tyler Bowers\nGithub.com/tylerebowers\nTylerebowers.com',
                                anchor="e", justify="center").grid(row=12, column=0, columnspan=2, rowspan=4)


        # Adjust window size and location
        screen_width = menu.winfo_screenwidth()
        screen_height = menu.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (windowWidth / 2))
        y_cordinate = int((screen_height / 2) - (windowHeight / 2))
        menu.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, x_cordinate, y_cordinate))
        menu.mainloop()

    def changeOrigin(self):
        if self.originButton.cget("text") == "Top Left":
            self.originButton.config(text="Bottom Left")
            self.origin = "BL"
            for b in self.quickButtons:
                b.config(text=f"{b.cget('text')[:-2]}{self.origin}")
        else:
            self.originButton.config(text="Top Left")
            self.origin = "TL"
            for b in self.quickButtons:
                b.config(text=f"{b.cget('text')[:-2]}{self.origin}")


if __name__ == '__main__':
    menu()
