import customtkinter as ctk
from CTkListbox import CTkListbox
import os
from nouvelle_trajectoire import NewTrajectory
from edit_trajectoire import EditTrajectory
import datetime
from tcp_ip_advance.computer import TCPClient
import tkinter as tk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trajectoires")

        # Label au-dessus de la liste
        self.label = ctk.CTkLabel(self, text="TRAJECTOIRES", font=("Arial", 20))
        self.label.pack(pady=10)

        self.robot_connection_var = tk.StringVar()
        self.robot_connection_var.set("Connection au robot ")

        self.robot_connection = ctk.CTkLabel(self, text="Connection au robot ", font=("Arial", 14))
        self.robot_connection.pack(pady=5)

        self.pick_trajectory = ctk.CTkLabel(self, text="Choissisez une trajectoire existante", font=("Arial", 12))
        self.pick_trajectory.pack(pady=5)

        self.listbox = CTkListbox(self, command=self.open_trajectory_edit, font=("Arial", 14))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.folder_path = "./Trajectoires"  
        self.refresh_listbox()

        self.add_trajectory_txt = ctk.CTkLabel(self, text=f"Ajouter une nouvelle trajectoire", font=("Arial", 12))
        self.add_trajectory_txt.pack(pady=15)

        self.add_button = ctk.CTkButton(self, text="+", command=self.on_add_button_click, font=("Arial", 25))
        self.add_button.pack(pady=10, ipadx=10)

        self.center_window(500, 625)

        self.robot = None
        self.start_robot_connection()
    
    def add_text_log(self, text):
        self.robot_connection_var.set(self.robot_connection_var.get() + text)
    
    def start_robot_connection(self):
        ip, port = "192.168.127.100", 20002
        self.add_text_log(f"{ip}:{port}")
        try:
            self.robot = TCPClient(ip, port)
        except Exception as ex:
            self.add_text_log(f", Erreur connexion : {ex}")
            return
        response = self.robot.hi()
        if not response:
            self.add_text_log(f", Erreur dialogue : {response}")
            return
        self.add_text_log(f", Ok")

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
        edit_trajectory_window = EditTrajectory(self, self.robot, self.call_back_refresh, self.listbox.curselection(), self.folder_path, [file.split(".")[:-1][0] for file in os.listdir(self.folder_path) if file.endswith(".json")])
        self.grab_set()
        edit_trajectory_window.mainloop()
        self.grab_release()

    def on_add_button_click(self):
        add_window = NewTrajectory(self, self.robot, self.call_back_refresh, self.folder_path)
        add_window.mainloop()
    
    def call_back_refresh(self):
        self.refresh_listbox()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    main_window = MainWindow()
    main_window.mainloop()