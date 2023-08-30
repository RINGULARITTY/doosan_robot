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

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trajectoires")
        center_right_window(self, 575, 700)

        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="TRAJECTOIRES", font=font, text_color="#327DFF").pack(pady=10)

        self.robot_connection = ctk.CTkLabel(self, text="Connexion au robot...", font=("Arial", 10))
        self.robot_connection.pack(pady=5)

        ctk.CTkLabel(self, text="Choisissez une trajectoire existante").pack(pady=5)

        self.listbox = CTkListbox(self, command=self.open_trajectory_edit)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.folder_path = resource_path(resource_path("./fichiers_trajectoires"))  
        self.refresh_listbox()

        ctk.CTkLabel(self, text=f"Ajouter une nouvelle trajectoire").pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="+", command=self.on_add_button_click, font=("Arial", 25))
        self.add_button.pack(pady=5, ipadx=10)

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


if __name__ == "__main__":
    ctk.set_default_color_theme(resource_path("Office_Like.json"))
    ctk.set_appearance_mode("light")
    main_window = MainWindow()
    main_window.iconbitmap(resource_path("./icon.ico"))
    main_window.mainloop()