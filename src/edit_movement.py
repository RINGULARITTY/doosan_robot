import customtkinter as ctk
from trajectory_lib import Trajectory, Movement
from password import Password
from tkinter import messagebox
from path_changer import resource_path
from tcp_ip_advance.computer import TCPClient
from typing import List
from window_tools import center_right_window

class EditMovement(ctk.CTkToplevel):
    def __init__(self, master, robot, callback, trajectory: Trajectory, movement_index):
        super().__init__(master)

        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))

        self.title("Editeur Mouvement")
        center_right_window(self, 650, 600)
        
        self.robot: TCPClient = robot
        self.callback = callback
        
        self.trajectory: Trajectory = trajectory
        self.movement_index = movement_index
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="MOUVEMENT", font=font, text_color="#327DFF").pack(pady=10)
        
        movement = self.trajectory.trajectory[self.movement_index]
        
        self.coords: List[List[ctk.CTkEntry]] = []
        self.frames, self.change_coord = [], []
        for i, c in enumerate(movement.coords):
            self.frames.append(ctk.CTkFrame(self))
            self.frames[-1].pack(padx=10)

            ctk.CTkLabel(self.frames[-1], text=f"Position Point {i + 1}", font=("Arial", 12)).pack()

            fs = []
            for j in range(3):
                ctk.CTkLabel(self.frames[-1], text=["X", "Y", "Z"][j]).pack(side="left", padx=3, pady=5)
                
                fs.append(ctk.CTkEntry(self.frames[-1], width=75))
                fs[-1].pack(side="left", padx=5, pady=5)
                fs[-1].insert(0, f"{c.get_with_index(j)}")
                fs[-1].configure(state="disabled")
            
            self.coords.append(fs)
            
            self.change_coord.append(ctk.CTkButton(self.frames[-1], text="Nouvelle prise", command=lambda: self.on_new_take(i), width=100))
            self.change_coord[-1].pack(side="left", padx=5)
            
        
        match movement.nature:
            case Movement.ORIGIN | Movement.APPROACH_POINT | Movement.PASS | Movement.CLEARANCE:
                self.wield_frame = None
            case _:
                self.wield_frame = ctk.CTkFrame(self)
                self.wield_frame.pack(padx=5, pady=10)
                self.wield_label = ctk.CTkLabel(self.wield_frame, text="Taille cordon")
                self.wield_label.pack(side="left", padx=5)
                self.wield = ctk.CTkEntry(self.wield_frame)
                self.wield.insert(0, f"{movement.wield_width}")
                self.wield.pack(side="left")
        
        self.space = ctk.CTkLabel(self, text="")
        self.space.pack()
            
        ctk.CTkLabel(self, text="Changer les coordonées").pack(pady=5)

        ctk.CTkButton(self, text="A la main", command=self.on_hand_change).pack(padx=10)
        
        self.save = ctk.CTkButton(self, text="Sauvegarder", command=self.on_save)
        self.save.pack(pady=10)
      
    def on_new_take(self, index):
        self.robot.wait_manual_guide()
        position = self.robot.get_current_posx()[0]
        for i in range(3):
            self.coords[index][i].configure(textvariable=f"{position[i]}")
    
    def on_hand_change(self):
        password = Password(self, self.password_callback)
        password.mainloop()
        
    def password_callback(self, res):
        if res:
            print(len(self.coords))
            for coord in self.coords:
                print(len(coord))
                for c in coord:
                    c.configure(state="normal")
    
    def on_save(self):
        for i in range(len(self.trajectory.trajectory[self.movement_index].coords)):
            for j in range(3):
                try:
                    float(self.coords[i][j].get())
                except:
                    messagebox.showerror(
                        title="Erreur", 
                        icon="error", 
                        message=f"Coordonée invalide pour le point {i + 1} pour la coordonée {['x', 'y', 'z'][j]} : {self.coords[i][j].get()}"
                    )
                    return
        
        if self.wield_frame != None:
            try:
                wield_width = int(self.wield.get())
                assert wield_width in [0, 3, 4, 5, 6, 8, 6, 8, 10, 12]
                self.trajectory.trajectory[self.movement_index].wield_width = wield_width
            except:
                messagebox.showerror(
                    title="Erreur", 
                    icon="error", 
                    message=f"Taille de cordon incorrecte : {self.wield.get()}"
                )
                return
        
        for i in range(len(self.trajectory.trajectory[self.movement_index].coords)):
            self.trajectory.trajectory[self.movement_index].coords[i].x = float(self.coords[i][0].get())
            self.trajectory.trajectory[self.movement_index].coords[i].y = float(self.coords[i][1].get())
            self.trajectory.trajectory[self.movement_index].coords[i].z = float(self.coords[i][2].get())

        self.trajectory.compile(self.robot)
        self.callback()
        self.after(250, self.destroy)

if __name__ == '__main__':
    EditMovement(ctk.CTk(), None, lambda : 0, Trajectory.load("./fichiers_trajectoires/test_move.json"), 1).mainloop()