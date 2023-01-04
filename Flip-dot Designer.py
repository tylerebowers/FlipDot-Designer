import tkinter as tk

debug = False

def power(b, e):
    if e == 0: return 1
    if e == 1: return b
    if e >= 2: return b * power(b, e-1)

def dotEditor(numRows=112, numCols=16):
    class button_box:
        def __init__(self, button, ID_number):
            self.ID_number = ID_number
            self.button = button

        def off(self):
            self.button.config(bg="black")

        def on(self):
            self.button.config(bg="yellow")

        def isOn(self):
            if self.button.config('bg')[-1] == "yellow":
                return True
            else:
                return False

        def getX(self):
            return int(self.button.config('text')[-1].split(",")[0])

        def gety(self):
            return int(self.button.config('text')[-1].split(",")[1])

        def toggle(self, event):
            if self.button.config('bg')[-1] == "black":
                if debug: print(f'Button {self.ID_number} toggled ON.')
                self.on()
            else:
                if debug: print(f'Button {self.ID_number} toggled OFF.')
                self.off()

    button_list = []
    editor = tk.Tk()
    windowHeight = (numRows * 40) + 60
    windowWidth = (numCols * 46) + 16
    if windowHeight > editor.winfo_screenheight(): windowHeight = editor.winfo_screenheight() - 100
    if windowWidth > editor.winfo_screenwidth(): windowWidth = editor.winfo_screenwidth() - 50
    editor.geometry(str(windowWidth) + "x" + str(windowWidth))
    editor.title("Flip-dot Design Canvas")

    # Scrollbar
    canvas = tk.Canvas(editor, borderwidth=0, background="#ffffff")
    inside_frame = tk.Frame(canvas, background="#ffffff")
    vsb = tk.Scrollbar(editor, orient="vertical", command=canvas.yview)
    hsb = tk.Scrollbar(editor, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4, 4), window=inside_frame, anchor="nw")
    inside_frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

    # Functions for toolbar buttons
    def allOn():
        if debug: print("Button ALL toggled ON.")
        for but in button_list:
            but.on()

    def allOff():
        if debug: print("Button ALL toggled OFF.")
        for but in button_list:
            but.off()

    def importArray():
        arrayToImport = inside_frame.children.get("!entry").get().replace("{", "").replace("}", "").replace(";",
                                                                                                            "").replace(
            " ", "").split(",")
        if debug: print("IMPORTING: " + str(arrayToImport))
        if arrayToImport is not None and len(arrayToImport) > 1:
            for x in range(numCols):
                for y in range(numRows):
                    if x < len(arrayToImport) and (int(arrayToImport[x]) >> y) & 1:
                        for but in button_list:  # I am well-aware that this is not efficient at all
                            if but.getX() == x and but.gety() == y:
                                but.on()  # should just do the math to find the button's location in the list instead

    def export():
        if debug: print("Button ALL exported:")
        toConvert = [[0] * numRows for i in range(numCols)]
        convertedArray = [0] * numCols
        for but in button_list:
            if but.isOn():
                toConvert[but.getX()][but.gety()] = 1
            else:
                toConvert[but.getX()][but.gety()] = 0
        for i in range(0, numCols):
            sum = 0
            for j in range(0, numRows):
                if (toConvert[i][j] == 1):
                    sum += power(2, j)
            convertedArray[i] = int(sum)
        output = "{"
        for i in range(0, numCols):
            output += str(convertedArray[i])
            if (i != numCols - 1): output += ", "
        output += "};"
        inside_frame.children.get("!entry").delete(0, 'end')
        inside_frame.children.get("!entry").insert(0, output)
        print(output)

    # Toolbar buttons
    textVal = tk.StringVar()
    exportBox = tk.Entry(inside_frame, textvariable=textVal, width=22, fg="black")
    exportBox.grid(row=0, column=5, columnspan=4)
    inside_frame.children.get("!entry").insert(0, "Imports/Exports here")
    button = tk.Button(inside_frame, width=5, height=1, text="(X,Y)", bg='grey', relief="flat")
    button.grid(row=0, column=0)
    button = tk.Button(inside_frame, width=5, height=1, text="All Off", bg='grey', command=allOff)
    button.grid(row=0, column=1)
    button = tk.Button(inside_frame, width=5, height=1, text="All On", bg='grey', command=allOn)
    button.grid(row=0, column=2)
    button = tk.Button(inside_frame, width=5, height=1, text="Import", bg='grey', command=importArray)
    button.grid(row=0, column=3)
    button = tk.Button(inside_frame, width=5, height=1, text="Export", bg='grey', command=export)
    button.grid(row=0, column=4)
    # button = tk.Button(inside_frame, width=5, height=1, text="Exit", bg='grey', command=editor.destroy)
    # button.grid(row=0, column=5)

    # Creates all needed buttons
    button_number = 1
    for y in range(numRows):
        for x in range(numCols):
            button = tk.Button(inside_frame, width=5, height=2, text=(str(x) + "," + str(y)), bg='black', fg='grey')
            button.grid(row=numRows - y, column=x)
            button_list.append(button_box(button, button_number))
            button.bind('<Button-1>', button_list[button_number - 1].toggle)
            button_number += 1

    # Adjust window size and location
    screen_width = editor.winfo_screenwidth()
    screen_height = editor.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (windowWidth / 2))
    y_cordinate = int((screen_height / 2) - (windowHeight / 2)) - 40
    editor.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, x_cordinate, y_cordinate))
    editor.mainloop()


def launchMenu():
    menu = tk.Tk()
    windowWidth = 250
    windowHeight = 300
    menu.geometry(str(windowWidth) + "x" + str(windowHeight))
    menu.title("Flip-dot Designer Menu")
    numCols = tk.IntVar()
    numRows = tk.IntVar()
    # importVal = tk.StringVar()
    titleLabel = tk.Label(menu, height=1, text="Flip-dot Designer", anchor="n", justify="center",font=("Helvetica", 20))
    presetsLabel = tk.Label(menu, height=1, text="Quick Buttons:", anchor="w", justify="left")
    # noteLabel = tk.Label(menu, height=1, text="*Quick buttons include imported array.", anchor="e", justify="left")
    emptyLabel1 = tk.Label(menu, height=1)
    emptyLabel2 = tk.Label(menu, height=1)
    emptyLabel3 = tk.Label(menu, height=1)
    rowLabel = tk.Label(menu, text='Number Of Rows:        ', anchor="w", justify="left")
    numRowBox = tk.Entry(menu, textvariable=numRows, width=16, justify="right")
    numRows.set(16)
    colLabel = tk.Label(menu, text='Number Of Columns:  ', anchor="w", justify="left")
    numColBox = tk.Entry(menu, textvariable=numCols, width=16, justify="right")
    numCols.set(112)
    # importLabel = tk.Label(menu, text='Import Array (optional):', anchor="w", justify="left")
    # importBox = tk.Entry(menu, textvariable=importVal, width=16, justify="right")
    # importVal.set("None")
    quickButton = tk.Button(menu, width=16, height=1, text="Launch 8R x 8C", bg='grey',
                            command=lambda: [menu.destroy, dotEditor(8, 8)])
    quickButton2 = tk.Button(menu, width=16, height=1, text="Launch 16R x 112C", bg='grey',
                             command=lambda: [menu.destroy, dotEditor(16, 112)])
    quickButton3 = tk.Button(menu, width=16, height=1, text="Launch 7R x 90C", bg='grey',
                             command=lambda: [menu.destroy, dotEditor(7, 90)])
    quickButton4 = tk.Button(menu, width=16, height=1, text="Launch 7R x 30C", bg='grey',
                             command=lambda: [menu.destroy, dotEditor(7, 30)])
    launch = tk.Button(menu, width=16, height=1, text="Launch", bg='grey',
                       command=lambda: [menu.destroy, dotEditor(numRows.get(), numCols.get())])
    creatorLabel = tk.Label(menu,
                            text='Flip-dot Designer    Version 1.2\nProgrammed by:  Tyler Bowers\nTylerebowers.com',
                            anchor="e", justify="center")

    titleLabel.grid(row=0, column=0, rowspan=2, columnspan=2)
    rowLabel.grid(row=2, column=0)
    numRowBox.grid(row=2, column=1)
    colLabel.grid(row=3, column=0)
    numColBox.grid(row=3, column=1)
    # importLabel.grid(row=2, column=0)
    # importBox.grid(row=2, column=1)
    launch.grid(row=4, column=1)
    emptyLabel1.grid(row=5, column=0)
    presetsLabel.grid(row=6, column=0)
    quickButton.grid(row=7, column=0)
    quickButton2.grid(row=7, column=1)
    quickButton3.grid(row=8, column=0)
    quickButton4.grid(row=8, column=1)
    # noteLabel.grid(row=8, column=0, columnspan=2)
    emptyLabel2.grid(row=9)
    emptyLabel3.grid(row=10)
    creatorLabel.grid(row=11, column=0, columnspan=2, rowspan=4)

    # Adjust window size and location
    screen_width = menu.winfo_screenwidth()
    screen_height = menu.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (windowWidth / 2))
    y_cordinate = int((screen_height / 2) - (windowHeight / 2))
    menu.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, x_cordinate, y_cordinate))
    menu.mainloop()


if __name__ == '__main__':
    launchMenu()
