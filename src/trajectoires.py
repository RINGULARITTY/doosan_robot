import customtkinter as ctk
from CTkListbox import CTkListbox
import os
from nouvelle_trajectoire import NewTrajectory
from edit_trajectoire import EditTrajectory
import datetime

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trajectoires")

        # Label au-dessus de la liste
        self.label = ctk.CTkLabel(self, text="TRAJECTOIRES", font=("Arial", 20))
        self.label.pack(pady=10)

        self.listbox = CTkListbox(self, command=self.open_trajectory_edit, font=("Arial", 14))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.folder_path = "./Trajectoires"  
        self.refresh_listbox()

        self.add_button = ctk.CTkButton(self, text="+", command=self.on_add_button_click, font=("Arial", 25))
        self.add_button.pack(pady=10, ipadx=10)

        self.center_window(400, 600)

    def refresh_listbox(self):
        self.listbox.delete("all")
        for file in os.listdir(self.folder_path):
            if file.endswith(".json"):
                self.listbox.insert(
                    "END",
                    os.path.splitext(file)[0] +
                        "  -  " +
                        datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.folder_path, file))).strftime('%Y-%m-%d %H:%M:%S')
                )

    def center_window(self, width=None, height=None):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if width is None:
            width = self.winfo_width()
        if height is None:
            height = self.winfo_height()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def open_trajectory_edit(self, _):
        folder_path = "./Trajectoires"
        edit_trajectory_window = EditTrajectory(self, self.call_back_trajectory_edit, self.listbox.curselection(), folder_path, [file.split(".")[:-1][0] for file in os.listdir(folder_path) if file.endswith(".json")])
        self.grab_set()
        edit_trajectory_window.mainloop()
        self.grab_release()
        

    def call_back_trajectory_edit(self):
        self.refresh_listbox()

    def on_add_button_click(self):
        add_window = NewTrajectory(self)
        add_window.mainloop()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    main_window = MainWindow()
    main_window.mainloop()