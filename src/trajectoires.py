import customtkinter as ctk
from CTkListbox import CTkListbox
import os
from nouvelle_trajectoire import NewTrajectory
from edit_trajectoire import EditTrajectory
import datetime
from tcp_ip_advance.computer import TCPClient
import json
from path_changer import resource_path

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trajectoires")

        self.label = ctk.CTkLabel(self, text="TRAJECTOIRES", font=("Arial", 20))
        self.label.pack(pady=10)

        self.robot_connection = ctk.CTkLabel(self, text="Connexion au robot...", font=("Arial", 14))
        self.robot_connection.pack(pady=5)

        self.pick_trajectory = ctk.CTkLabel(self, text="Choisissez une trajectoire existante", font=("Arial", 12))
        self.pick_trajectory.pack(pady=5)

        self.listbox = CTkListbox(self, command=self.open_trajectory_edit, font=("Arial", 14))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.folder_path = resource_path(resource_path("./fichiers_trajectoires"))  
        self.refresh_listbox()

        self.add_trajectory_txt = ctk.CTkLabel(self, text=f"Ajouter une nouvelle trajectoire", font=("Arial", 12))
        self.add_trajectory_txt.pack(pady=15)

        self.add_button = ctk.CTkButton(self, text="+", command=self.on_add_button_click, font=("Arial", 25))
        self.add_button.pack(pady=10, ipadx=10)

        self.center_window(500, 625)

        self.robot = None
        self.after(500, self.start_robot_connection())

    def set_text_log(self, text):
        self.robot_connection.configure(text=text)
    
    def start_robot_connection(self):
        with open(resource_path("./config.json"), "r") as f:
            config = json.load(f)

        ip, port = config['robot']['ip'], config['robot']['port']
        try:
            self.robot = TCPClient(ip, port)
        except Exception as ex:
            self.set_text_log(f"Erreur connexion robot : {ex}")
            return
        response = self.robot.hi()
        if not response:
            self.set_text_log(f"Erreur dialogue robot : {response}")
            return
        self.set_text_log(f", Robot connecté")

    def refresh_listbox(self):
        self.listbox.delete("all")
        for file in os.listdir(self.folder_path):
            if file.endswith(".json"):
                self.listbox.insert(
                    "END",
                    os.path.splitext(file)[0] +
                        "  -  " +
                        datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.folder_path, file))).strftime('%d-%m-%Y %H:%M')
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
        edit_trajectory_window.mainloop()

    def on_add_button_click(self):
        add_window = NewTrajectory(self, self.robot, self.call_back_refresh, self.folder_path)
        add_window.mainloop()
    
    def call_back_refresh(self):
        self.refresh_listbox()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    main_window = MainWindow()
    main_window.iconbitmap(resource_path("./icon.ico"))
    main_window.mainloop()