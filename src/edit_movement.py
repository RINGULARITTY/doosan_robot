import customtkinter as ctk
from trajectory_lib import Trajectory, Movement
from password import Password
from tkinter import messagebox
from path_changer import resource_path
from tcp_ip_advance.computer import TCPClient
from typing import List
from window_tools import center_right_window
from material_builder import Materials

class EditMovement(ctk.CTkToplevel):
    def __init__(self, master, robot, callback, trajectory: Trajectory, movement_index):
        super().__init__(master)

        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))

        self.title("Editeur Mouvement")
        center_right_window(self, 500, 600)
        
        self.robot: TCPClient = robot
        self.callback = callback
        
        self.trajectory: Trajectory = trajectory
        self.movement_index = movement_index
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="MOUVEMENT", font=font, text_color="#327DFF").pack(pady=10)
        
        movement = self.trajectory.trajectory[self.movement_index]
        
        ctk.CTkLabel(self, text=f"Movement {Movement.TRANSLATIONS[movement.nature]}", font=("Arial", 16)).pack(pady=10)
        
        self.coords: List[List[ctk.CTkLabel]] = []
        self.frames, self.change_coord = [], []
        for i, c in enumerate(movement.coords):
            self.frames.append(ctk.CTkFrame(self))
            self.frames[-1].pack(pady=5)

            ctk.CTkLabel(self.frames[-1], text=f"Position Point {i + 1}", font=("Arial", 12)).pack()

            fs = []
            for j in range(3):
                ctk.CTkLabel(self.frames[-1], text=["X", "Y", "Z"][j]).pack(side="left", padx=3, pady=5)
                
                fs.append(ctk.CTkLabel(self.frames[-1], text=c.get_with_index(j), width=75))
                fs[-1].pack(side="left", padx=5, pady=5)
            
            self.coords.append(fs)
            
            self.change_coord.append(ctk.CTkButton(self.frames[-1], text="Nouvelle prise", command=lambda: self.on_new_take(i), width=75))
            self.change_coord[-1].pack(padx=5)

        
        match movement.nature:
            case Movement.ORIGIN | Movement.APPROACH_POINT | Movement.PASS | Movement.CLEARANCE:
                self.wield_frame = None
            case _:
                self.wield_frame = ctk.CTkFrame(self)
                self.wield_frame.pack(padx=5, pady=10)
                self.wield_label = ctk.CTkLabel(self.wield_frame, text="Taille cordon")
                self.wield_label.pack(side="left", padx=5)
                self.wield = ctk.CTkComboBox(self.wield_frame, values=[str(ww) for ww in Materials.WIELD_WIDTHS])
                self.wield.set(f"{movement.wield_width}")
                self.wield.pack(side="left")
        
        ctk.CTkLabel(self, text="").pack()
        
        ctk.CTkLabel(self, text="Ajouter aux coordonnées existantes", font=('Arial', 16)).pack(pady=5)
        
        self.coords_edit: List[List[ctk.CTkEntry]] = []
        self.frames_edit, self.change_landmark = [], []
        for i, c in enumerate(movement.coords):
            self.frames_edit.append(ctk.CTkFrame(self))
            self.frames_edit[-1].pack(pady=5)

            ctk.CTkLabel(self.frames_edit[-1], text=f"Position Point {i + 1}", font=("Arial", 12)).pack()

            fs = []
            for j in range(3):
                ctk.CTkLabel(self.frames_edit[-1], text=["X", "Y", "Z"][j]).pack(side="left", padx=3, pady=5)
                
                fs.append(ctk.CTkEntry(self.frames_edit[-1], width=75))
                fs[-1].insert(0, "0")
                fs[-1].pack(side="left", padx=5, pady=5)
            
            self.coords_edit.append(fs)
            
            self.change_landmark.append(ctk.CTkComboBox(self.frames_edit[-1], values=["Base", "Outil"], width=85))
            self.change_landmark[-1].pack(padx=10, side="left")
        
        self.save_new = ctk.CTkButton(self, text="Ajouter", command=self.add_coords, width=75)
        self.save_new.pack(pady=25)
        
        self.save = ctk.CTkButton(self, text="Sauvegarder", command=self.on_save, width=100)
        self.save.pack(pady=5)
    
    
    def on_new_take(self, index):
        self.robot.wait_manual_guide()
        position = self.robot.get_current_posx()[0]
        for i in range(3):
            self.coords[index][i].configure(textvariable=f"{position[i]}")
    
    def add_coord_pw(self):
        Password(self, callback=self.add_coords)
    
    def add_coords(self, res):
        if not res:
            return
        
        movement: Movement = self.trajectory.trajectory[self.movement_index]
        
        for i, c in enumerate(movement.coords):
            for j, ce in enumerate(self.coords_edit[i]):
                try:
                    float(ce.get())
                except:
                    messagebox.showerror(
                        title="Erreur", 
                        icon="error", 
                        message=f"Ajout invalide pour le point {i + 1} pour la coordonée {['x', 'y', 'z'][j]} : {ce.get()}"
                    )
                    return
        
        for i, c in enumerate(movement.coords):
            if self.change_landmark[i].get() == "Base":
                for j, ce in enumerate(self.coords_edit[i]):
                    coord = self.coords[i][j]
                    coord.configure(text=f"{float(coord._text) + float(ce.get())}")
            elif self.change_landmark[i].get() == "Outil":
                new_pos = self.robot.offset([
                    float(self.coords[i][0]._text),
                    float(self.coords[i][1]._text),
                    float(self.coords[i][2]._text),
                    c.a, c.b, c.c,
                    float(self.coords_edit[i][0].get()),
                    float(self.coords_edit[i][1].get()),
                    float(self.coords_edit[i][2].get())
                ])
                for j, c in enumerate(self.coords[i]):
                    self.coords[i][j].configure(text=f"{new_pos[j]}")
                
            for j, ce in enumerate(self.coords_edit[i]):
                ce.delete(0, "end")
                ce.insert(0, "0")

        self.coords[0][0].focus()     
        
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
                    float(self.coords[i][j]._text)
                except:
                    messagebox.showerror(
                        title="Erreur", 
                        icon="error", 
                        message=f"Coordonée invalide pour le point {i + 1} pour la coordonée {['x', 'y', 'z'][j]} : {self.coords[i][j].get()}"
                    )
                    return
        
        if self.wield_frame != None:
            self.trajectory.trajectory[self.movement_index].wield_width = float(self.wield.get())
        
        for i in range(len(self.trajectory.trajectory[self.movement_index].coords)):
            self.trajectory.trajectory[self.movement_index].coords[i].x = float(self.coords[i][0]._text)
            self.trajectory.trajectory[self.movement_index].coords[i].y = float(self.coords[i][1]._text)
            self.trajectory.trajectory[self.movement_index].coords[i].z = float(self.coords[i][2]._text)

        self.trajectory.compile(self.robot)
        self.callback()
        self.after(250, self.destroy)

if __name__ == '__main__':
    EditMovement(ctk.CTk(), None, lambda : 0, Trajectory.load("./fichiers_trajectoires/test_move.json"), 3).mainloop()