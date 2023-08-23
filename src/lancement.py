import customtkinter as ctk
from trajectory_lib import Trajectory
import time

class Run(ctk.CTkToplevel):
    def __init__(self, master, trajectory):
        super().__init__()
        self.title("Ajouter un élément")
        self.geometry("450x700")
        
        self.trajectory: Trajectory = trajectory
        
        self.label3 = ctk.CTkLabel(self, text="Lancement", font=("Arial", 20))
        self.label3.pack(pady=10)
        
        self.label4 = ctk.CTkLabel(self, text=f"Trajectoire choisie : {self.trajectory.name}", font=("Arial", 14))
        self.label4.pack(pady=5)
        
        self.label5 = ctk.CTkLabel(self, text="Choisissez le nombre de pièces à produire", font=("Arial", 14))
        self.label5.pack(pady=5)
        
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=10)
        
        self.button2 = ctk.CTkButton(self, text="Lancer", command=self.run)
        self.button2.pack(pady=20)
        
        self.label6 = ctk.CTkLabel(self, text="Avancement", font=("Arial", 14))
        self.label6.pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self, state='disabled', height=200, font=("Arial", 14))
        self.textbox.pack(padx=5, fill="both", expand=True)
        self.textbox.configure(state='normal')
        
        self.textbox.configure(state='disabled')
        
        
    def combobox_callback(self):
        pass
    
    def run(self):
        self.textbox.delete("all")
        translations = {"START": "Début", "LINEAR": "Linéaire", "CIRCULAR": "Circulaire", "PASS": "Passage"}
        for m in self.trajectory.trajectory:
            self.textbox.configure(state='normal')
            self.textbox.insert("end", f"{translations[m.nature]}, {m.config}, {m.str_coords_pos()}\n")
            self.textbox.configure(state='disabled')