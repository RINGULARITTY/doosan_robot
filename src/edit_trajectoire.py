import customtkinter as ctk
from CTkListbox import CTkListbox
from trajectory_lib import Trajectory
from password import Password
import os
from tkinter import messagebox
from lancement import Run

class EditMovement(ctk.CTkToplevel):
    def __init__(self, master, callback, trajectory: Trajectory, movement_index):
        super().__init__()

        self.title("Editeur Mouvement")
        self.geometry("600x350")
        
        self.callback = callback
        
        self.trajectory = trajectory
        self.movement_index = movement_index
        
        self.title_label = ctk.CTkLabel(self, text="Mouvement", font=("Arial", 20))
        self.title_label.pack(pady=10)
        
        movement = self.trajectory.trajectory[self.movement_index]
        
        self.frames, self.titles, self.labels, self.coords = [], [], [], []
        for i, c in enumerate(movement.coords):
            self.frames.append(ctk.CTkFrame(self))
            self.frames[-1].pack()

            self.titles.append(ctk.CTkLabel(self.frames[-1], text=f"Position Point {i+1}", font=("Arial", 12)))
            self.titles[-1].pack()

            ls, fs = [], []
            for j in range(3):
                ls.append(ctk.CTkLabel(self.frames[-1], text=["X", "Y", "Z"][j], font=("Arial", 14)))
                ls[-1].pack(side="left", padx=5, pady=5)
                
                fs.append(ctk.CTkEntry(self.frames[-1], font=("Arial", 14)))
                fs[-1].pack(side="left", padx=10, pady=5)
                fs[-1].insert(0, c.get_with_index(j))
                fs[-1].configure(state="disabled")
            
            self.labels.append(ls)
            self.coords.append(fs)
        
        self.space = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.space.pack()
            
        self.change_coord = ctk.CTkLabel(self, text="Changer les coordonées", font=("Arial", 14))
        self.change_coord.pack(pady=5)
        
        self.frame3 = ctk.CTkFrame(self)
        self.frame3.pack(pady=10)
        self.new_take = ctk.CTkButton(self.frame3, text="Nouvelle prise", command=self.on_new_take, font=("Arial", 14))
        self.new_take.pack(side="left", padx=10)

        self.hand_change = ctk.CTkButton(self.frame3, text="A la main", command=self.on_hand_change, font=("Arial", 14))
        self.hand_change.pack(side="left", padx=10)
        
        self.save = ctk.CTkButton(self, text="Savegarder", command=self.on_save, font=("Arial", 14))
        self.save.pack(pady=10)
      
    def on_new_take(self):
        pass
    
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
            self.trajectory.trajectory[self.movement_index].coords[i].x = float(self.coords[i][0].get())
            self.trajectory.trajectory[self.movement_index].coords[i].y = float(self.coords[i][1].get())
            self.trajectory.trajectory[self.movement_index].coords[i].z = float(self.coords[i][2].get())

        self.callback()
        self.after(250, self.destroy)

class EditTrajectory(ctk.CTkToplevel):
    def __init__(self, master, callback, selected_index, folder_path, trajectories):
        super().__init__()
        
        self.folder_path = folder_path
        self.callback = callback
        
        self.title("Editeur Trajectoire")
        self.geometry("775x575")
        
        self.trajectory: Trajectory = Trajectory.load(os.path.join(self.folder_path, trajectories[selected_index] + ".json"))
        
        self.name_entry = ctk.CTkEntry(self, font=("Arial", 20), width=250)
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, self.trajectory.name)

        self.title_label = ctk.CTkLabel(self, text="Mouvements", font=("Arial", 14))
        self.title_label.pack(pady=5)

        self.listbox = CTkListbox(self, command=self.on_list_click)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_listbox()

        self.frame1 = ctk.CTkFrame(self)
        self.frame1.pack()
        self.run = ctk.CTkButton(self.frame1, text="Lancer", command=self.on_run, font=("Arial", 14))
        self.run.pack(side="left", padx=5, pady=10)
        self.save = ctk.CTkButton(self.frame1, text="Sauvegarder", command=self.on_save, font=("Arial", 14))
        self.save.pack(side="left", padx=5, pady=10)

    def refresh_listbox(self):
        self.listbox.delete("all")
        translations = {"START": "Début", "LINEAR": "Linéaire", "CIRCULAR": "Circulaire", "PASS": "Passage"}
        for m in self.trajectory.trajectory:
            self.listbox.insert("END", f"{translations[m.nature]}, {m.config}, {m.str_coords_pos()}")

    def on_list_click(self, _):
        edit_move = EditMovement(self, self.on_move_edit_closed, self.trajectory, self.listbox.curselection())
        edit_move.mainloop()
        self.slaves(edit_move)
    
    def on_move_edit_closed(self):
        self.trajectory.compile()
        self.refresh_listbox()
        
    def on_run(self):
        run = Run(self, self.trajectory)
        run.mainloop()

    def on_save(self):
        response = messagebox.askyesno(
            title="Confirmation", 
            icon="warning", 
            message="Êtes-vous sûr de vouloir sauvegarder la trajectoire ?"
        )
        if not response:
            return

        if self.trajectory.name != self.name_entry.get():
            if os.path.exists(os.path.join(self.folder_path, self.name_entry.get() + ".json")):
                response = messagebox.showerror(
                    title="Erreur", 
                    icon="error", 
                    message=f"Une trajectoire au nom de {self.name_entry.get()} existe déjà"
                )
                return
            os.remove(os.path.join(self.folder_path, self.trajectory.name + ".json"))
            self.trajectory.name = self.name_entry.get()
        self.trajectory.save(self.folder_path)
        self.callback()
        self.after(250, self.destroy())