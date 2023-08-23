import tkinter as tk

class MainWindow:

    def __init__(self, master):
        self.master = master

        self.list_of_tasks = []

        self.new_task = tk.Button(self, bg="yellow", text="issou", command=self.create_new_task)
        self.new_task.grid(row=1, column=0)

    def create_new_task(self):
        #Creates a new task
        new_window = tk.Toplevel(self.master)
        entry_window = Task_Entry(new_window)

        entry_window.test_entry_field.wait_window(entry_window)

class Task_Entry:
    #Window for entering data into a new window
    def __init__(self, master):
        self.master = master

        self.test_entry_field = tk.Entry(self.master)
        self.test_entry_field.pack()
        self.test_entry = self.test_entry_field.get()

        self.cancel_button = tk.Button(self.master, text="Cancel", command=self.exit_program)
        self.cancel_button.pack()

    def exit_program(self):
        self.master.destroy()


root = tk.Tk()
gui = MainWindow(root)
root.mainloop()