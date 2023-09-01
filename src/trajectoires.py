import customtkinter as ctk
from CTkListbox import CTkListbox
import os
from nouvelle_trajectoire import NewTrajectory
from edit_trajectoire import EditTrajectory
from datetime import datetime
from tcp_ip_advance.computer import TCPClient
import json
from path_changer import resource_path
from window_tools import center_right_window
import shutil
import textwrap
from settings import Settings

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trajectoires")
        center_right_window(self, 600, 700)

        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="TRAJECTOIRES", font=font, text_color="#327DFF").pack(pady=10)

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(side="top", pady=10, fill="both", expand=False)
        
        ctk.CTkButton(self.frame, text="Paramètres", command=self.start_settings).pack(side="left", padx=5)
        ctk.CTkButton(self.frame, text="Connexion au robot", command=self.start_robot_connection).pack(side="left", padx=5)
        
        font = ctk.CTkFont("Arial", 10, weight="bold")
        self.robot_connection = ctk.CTkLabel(self.frame, text="Robot non conecté", font=font, text_color="#E60F00")
        self.robot_connection.pack(side="left", pady=5)

        ctk.CTkLabel(self, text="Choisissez une trajectoire existante").pack(pady=5)

        self.listbox = CTkListbox(self, command=self.open_trajectory_edit)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.folder_path = resource_path(resource_path("./fichiers_trajectoires"))  
        self.refresh_listbox()

        ctk.CTkLabel(self, text=f"Ajouter une nouvelle trajectoire").pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="+", command=self.on_add_button_click, font=("Arial", 25))
        self.add_button.pack(pady=5, ipadx=10)

        self.robot = None

    def set_text_log(self, text):
        self.robot_connection.configure(text=text)

    def start_settings(self):
        Settings(self).mainloop()
    
    def start_robot_connection(self):
        with open(resource_path("./config.json"), "r") as f:
            config = json.load(f)

        ip, port = config['robot']['ip'], config['robot']['port']
        try:
            self.robot = TCPClient(ip, port)
        except Exception as ex:
            self.set_text_log('\n'.join(textwrap.wrap(f"Erreur connexion robot : {ex}", 55)))
            return
        response = self.robot.hi()
        if not response:
            self.set_text_log('\n'.join(textwrap.wrap(f"Erreur dialogue robot : {response}", 55)))
            return
        self.set_text_log(f"Robot connecté")

    def refresh_listbox(self):
        self.listbox.delete("all")
        for file in os.listdir(self.folder_path):
            if file.endswith(".json"):
                self.listbox.insert(
                    "END",
                    os.path.splitext(file)[0] +
                        "  -  " +
                        datetime.fromtimestamp(os.path.getmtime(os.path.join(self.folder_path, file))).strftime('%d-%m-%Y %H:%M')
                )

    def open_trajectory_edit(self, _):
        edit_trajectory_window = EditTrajectory(self, self.robot, self.call_back_refresh, self.listbox.curselection(), self.folder_path, [file.split(".")[:-1][0] for file in os.listdir(self.folder_path) if file.endswith(".json")])
        edit_trajectory_window.mainloop()

    def on_add_button_click(self):
        add_window = NewTrajectory(self, self.robot, self.call_back_refresh, self.folder_path)
        add_window.mainloop()
    
    def call_back_refresh(self):
        self.refresh_listbox()


def make_backup():
    trajectories_folder = resource_path("fichiers_trajectoires")
    backup_folder = resource_path("backup")
    for tf in [f for f in os.listdir(trajectories_folder) if f.endswith('.json')]:
        shutil.copy(os.path.join(trajectories_folder, tf), os.path.join(backup_folder, tf))


if __name__ == "__main__":
    make_backup()
    ctk.set_default_color_theme(resource_path("Office_Like.json"))
    ctk.set_appearance_mode("light")
    main_window = MainWindow()
    main_window.iconbitmap(resource_path("./icon.ico"))
    main_window.mainloop()