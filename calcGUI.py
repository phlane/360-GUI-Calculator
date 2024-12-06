import tkinter as tk
import sys

sys.path.append('.')
from calcMain import parser, clearVars


class CalculatorGUI:
    def __init__(self, window):
        self.window = window
        window.title("Simple Calculator")
        self.main_frame = tk.Frame(window)
        self.main_frame.pack(padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, padx=5)

        self.entry = tk.Entry(self.left_frame, width=40, justify='right')
        self.entry.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        self.entry.focus_set()

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '%', '^', '+',
            '(',')'
        ]

        row = 1
        col = 0
        for button in buttons:
            if button == "Emp":
                tk.Label(self.left_frame, text="", width=7).grid(row=row, column=col, padx=3, pady=3)
            else:
                cmd = lambda x=button: self.click(x)
                tk.Button(self.left_frame, text=button, command=cmd, width=7).grid(row=row, column=col, padx=3, pady=3)

            col += 1
            if col > 3:
                col = 0
                row += 1

        tk.Button(self.left_frame, text='Clear', command=self.clear, width=7).grid(row=row, column=col, padx=3, pady=3)
        tk.Button(self.left_frame, text='Enter', command=self.calculate, width=7).grid(row=row, column=3, padx=3, pady=3)

        self.history_frame = tk.Frame(self.main_frame)
        self.history_frame.grid(row=0, column=1, padx=5)

        tk.Label(self.history_frame, text="History", font=('Arial', 14, 'bold')).pack()
        tk.Label(self.history_frame, text="(Double-click to replace,\n Right-click to insert)", font=('Arial', 10, 'italic'), fg="gray").pack()

        self.history_listbox = tk.Listbox(self.history_frame, width=40, height=10)
        self.history_listbox.pack(padx=5, pady=5)

        tk.Button(self.history_frame, text='Clear History', command=self.clearHistory).pack(pady=5)

        self.history_listbox.bind('<Double-1>', self.revertHistoryItem)

        self.var_frame = tk.Frame(self.main_frame)
        self.var_frame.grid(row=0, column=2, padx=5)

        tk.Label(self.var_frame, text="Variables", font=('Arial', 14, 'bold')).pack()
        tk.Label(self.var_frame, text="(Double-click to insert)\n", font=('Arial', 10, 'italic'), fg="gray").pack()


        self.var_listbox = tk.Listbox(self.var_frame, width=40, height=10)
        self.var_listbox.pack(padx=5, pady=5)
        self.var_listbox.bind('<Double-1>', self.revertHistoryItem)

        tk.Button(self.var_frame, text='Clear Variables', command=self.clearVariables).pack(pady=5)

        self.history = []
        self.variables = {}

        self.history_listbox.bind('<Double-1>', self.revertHistoryItem)
        self.history_listbox.bind('<Button-3>', self.insertHistoryItem)

        self.var_listbox.bind('<Double-1>', self.revertVarItem)

        window.bind('<Return>', self.enterPress)
        window.bind('<KP_Enter>', self.enterPress)
        window.bind('<BackSpace>', self.backspace)

    def enterPress(self, event=None):
        self.calculate()

    def click(self, key):
        if key == '=':
            self.calculate()
        elif key == '(':
            current_text = self.entry.get()
            if current_text and current_text[-1].isdigit():
                self.entry.insert(tk.END, '*(')
            else:
                self.entry.insert(tk.END, '(')
        else:
            self.window.unbind('<Key>')
            self.entry.insert(tk.END, key)

    def calculate(self):
        expression = self.entry.get()
        try:
            result = parser.parse(expression)
            if result is None:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Error")
                self.window.after(2000, self.clear)
            else:
                if '=' in self.entry.get():
                    self.entry.delete(0, tk.END)
                    var_entry = f"{expression}"

                    var = var_entry.split('=')[0].strip()
                    value = var_entry.split('=')[1].strip()

                    for i in range(self.var_listbox.size()):
                        existing_entry = self.var_listbox.get(i)
                        if existing_entry.startswith(var + ' ='):
                            self.var_listbox.delete(i)
                            break

                    new_var_entry = f"{var} = {value}"
                    self.var_listbox.insert(0, new_var_entry)

                    self.variables[var] = value
                else:
                    self.entry.delete(0, tk.END)
                    history_entry = f"{expression} = {result}"
                    self.history.insert(0, history_entry)
                    self.history_listbox.insert(0, history_entry)

                    if len(self.history) > 10:
                        self.history.pop()
                        self.history_listbox.delete(10)
        except Exception as e:
                        self.entry.config(state='normal')  # Ensure it's in normal state first
                        self.entry.delete(0, tk.END)
                        msg = ''
                        if str(e) == "var":
                            msg = "Unknown Variable"
                        else:
                            msg = "Generic Error"
                        self.entry.insert(0, msg)
                        self.entry.config(state='readonly')
                        self.window.after(2000, self.enableEntry)

    def enableEntry(self):
        self.entry.config(state='normal')
        self.clear()

    def revertHistoryItem(self, event):
        try:
            selection = self.history_listbox.curselection()[0]
            full_entry = self.history_listbox.get(selection)
            expression = full_entry.split(' =')[0]


            self.entry.delete(0, tk.END)
            self.entry.insert(0, expression)
        except IndexError:
            pass

    def insertHistoryItem(self, event):
            try:
                selection = self.history_listbox.curselection()[0]
                full_entry = self.history_listbox.get(selection)
                expression = full_entry.split(' =')[0]

                self.entry.insert(len(self.entry.get()), expression)
            except IndexError:
                pass

    def revertVarItem(self, event):
        try:
            selection = self.var_listbox.curselection()[0]
            full_entry = self.var_listbox.get(selection)
            expression = full_entry.split('=')[0]

            self.entry.insert(len(self.entry.get()), expression)
            self.entry.focus_set()
        except IndexError:
            pass

    def clear(self):
        self.entry.delete(0, tk.END)

    def clearHistory(self):
        self.history.clear()
        self.history_listbox.delete(0, tk.END)

    def clearVariables(self):
        self.var_listbox.delete(0, tk.END)
        clearVars()

    def backspace(self, event=None):
        current = self.entry.get()
        if current:
            self.entry.delete(len(current), tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x300")
    root.minsize(800,300)
    root.maxsize(1000,400)
    calculator = CalculatorGUI(root)
    root.mainloop()