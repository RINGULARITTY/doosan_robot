import customtkinter as ctk
from CTkListbox import CTkListbox
from trajectory_lib import Trajectory, Movement
from password import Password
import os
from tkinter import messagebox
from lancement import Run
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
        center_right_window(self, 650, 425)
        
        self.robot: TCPClient = robot
        self.callback = callback
        
        self.trajectory: Trajectory = trajectory
        self.movement_index = movement_index
        
        self.title_label = ctk.CTkLabel(self, text="Mouvement", font=("Arial", 20))
        self.title_label.pack(pady=10)
        
        movement = self.trajectory.trajectory[self.movement_index]
        
        self.coords: List[List[ctk.CTkEntry]] = []
        self.frames, self.titles, self.labels, self.change_coord = [], [], [], []
        for i, c in enumerate(movement.coords):
            self.frames.append(ctk.CTkFrame(self))
            self.frames[-1].pack(padx=10)

            self.titles.append(ctk.CTkLabel(self.frames[-1], text=f"Position Point {i + 1}", font=("Arial", 12)))
            self.titles[-1].pack()

            ls, fs = [], []
            for j in range(3):
                ls.append(ctk.CTkLabel(self.frames[-1], text=["X", "Y", "Z"][j], font=("Arial", 14)))
                ls[-1].pack(side="left", padx=3, pady=5)
                
                fs.append(ctk.CTkEntry(self.frames[-1], font=("Arial", 14)))
                fs[-1].pack(side="left", padx=5, pady=5)
                fs[-1].insert(0, f"{c.get_with_index(j)}")
                fs[-1].configure(state="disabled")
            
            self.labels.append(ls)
            self.coords.append(fs)
            
            self.change_coord.append(ctk.CTkButton(self.frames[-1], text="Nouvelle prise", command=lambda: self.on_new_take(i), font=("Arial", 14)))
            self.change_coord[-1].pack(side="left", padx=5)
        
        match movement.nature:
            case Movement.ORIGIN | Movement.APPROACH_POINT | Movement.PASS | Movement.CLEARANCE:
                self.wield_frame = None
            case _:
                self.wield_frame = ctk.CTkFrame(self)
                self.wield_frame.pack(padx=5, pady=10)
                self.wield_label = ctk.CTkLabel(self.wield_frame, text="Taille cordon", font=("Arial", 14))
                self.wield_label.pack(side="left", padx=5)
                self.wield = ctk.CTkEntry(self.wield_frame, font=("Arial", 14))
                self.wield.insert(0, f"{movement.wield_width}")
                self.wield.pack(side="left")
        
        self.space = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.space.pack()
            
        self.change_coord = ctk.CTkLabel(self, text="Changer les coordonées", font=("Arial", 14))
        self.change_coord.pack(pady=5)

        self.hand_change = ctk.CTkButton(self, text="A la main", command=self.on_hand_change, font=("Arial", 14))
        self.hand_change.pack(padx=10)
        
        self.save = ctk.CTkButton(self, text="Sauvegarder", command=self.on_save, font=("Arial", 14))
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