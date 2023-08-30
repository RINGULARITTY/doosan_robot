import customtkinter as ctk
from CTkListbox import CTkListbox
import os
from tkinter import messagebox
from lancement import Run
from path_changer import resource_path
from typing import List
from edit_movement import EditMovement
from window_tools import center_right_window
from trajectory_lib import Trajectory

class EditTrajectory(ctk.CTkToplevel):
    def __init__(self, master, robot, callback, selected_index, folder_path, trajectories):
        super().__init__()
        
        self.grab_set()
        
        self.robot = robot
        self.callback = callback
        self.folder_path = folder_path
        
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        
        self.title("Editeur Trajectoire")
        center_right_window(self, 650, 575)
        
        self.trajectory: Trajectory = Trajectory.load(os.path.join(self.folder_path, trajectories[selected_index] + ".json"))
        self.trajectory.compile(self.robot)
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        self.name_entry = ctk.CTkEntry(self, font=font, text_color="#327DFF", width=250)
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, self.trajectory.name)

        ctk.CTkLabel(self, text="Mouvements").pack(pady=5)

        self.listbox = CTkListbox(self, command=self.on_list_click)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_listbox()

        self.frame1 = ctk.CTkFrame(self)
        self.frame1.pack()
        self.run = ctk.CTkButton(self.frame1, text="Lancer", command=self.on_run)
        self.run.pack(side="left", padx=5, pady=10)
        self.save = ctk.CTkButton(self.frame1, text="Sauvegarder", command=self.on_save)
        self.save.pack(side="left", padx=5, pady=10)

    def refresh_listbox(self):
        self.listbox.delete("all")
        for m in self.trajectory.trajectory:
            self.listbox.insert("END", m.to_string())

    def on_list_click(self, _):
        edit_move = EditMovement(self, self.robot, self.on_move_edit_closed, self.trajectory, self.listbox.curselection())
        edit_move.mainloop()
        self.slaves(edit_move)
    
    def on_move_edit_closed(self):
        self.refresh_listbox()
        
    def on_run(self):
        run = Run(self, self.robot, self.trajectory)
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
            os.remove(os.path.join(self.folder_path, self.trajectory.name + ".json"))
            self.trajectory.name = self.name_entry.get()
            if not self.trajectory.save(self.folder_path):
                return
        else:
            if not self.trajectory.save(self.folder_path, True):
                return
        self.callback()
        self.after(250, self.destroy())