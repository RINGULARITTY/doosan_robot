import customtkinter as ctk
from path_changer import resource_path
from window_tools import center_right_window
import json
from password import Password
from tkinter import messagebox

class Settings(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        
        self.title("Paramètres")
        center_right_window(self, 650, 500)
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="PARAMETRES", font=font, text_color="#327DFF").pack(pady=10)
        
        with open(resource_path("config.json"), 'r') as f:
            self.config = json.load(f)
        
        self.frame1 = ctk.CTkFrame(self)
        self.frame1.pack(pady=10)
        
        ctk.CTkLabel(self.frame1, text="Connexion robot").pack()
        
        ctk.CTkLabel(self.frame1, text="Ip").pack(side="left", padx=5)
        self.ip_entry = ctk.CTkEntry(self.frame1)
        self.ip_entry.insert(0, self.config["robot"]["ip"])
        self.ip_entry.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.frame1, text="Port").pack(side="left", padx=5)
        self.port_entry = ctk.CTkEntry(self.frame1)
        self.port_entry.insert(0, f"{self.config['robot']['port']}")
        self.port_entry.pack(side="left", padx=10)
    
        self.frame2 = ctk.CTkFrame(self)
        self.frame2.pack(pady=10)
        
        ctk.CTkLabel(self.frame2, text="Coordonnées origine").pack()

        self.origin_coords = []
        for c in ["x", "y", "z", "a", "b", "c"]:
            ctk.CTkLabel(self.frame2, text=c).pack(side="left", padx=5)
            self.origin_coords.append(ctk.CTkEntry(self.frame2, width=65))
            self.origin_coords[-1].insert(0, f"{self.config['default_coords']['origin'][c]}")
            self.origin_coords[-1].pack(side="left", padx=10)
        
        self.frame3 = ctk.CTkFrame(self)
        self.frame3.pack(pady=10)
        
        ctk.CTkLabel(self.frame3, text="Offsets d'approche").pack()
        
        self.approach_coords = []
        for c in ["x_offset", "y_offset", "z_offset"]:
            ctk.CTkLabel(self.frame3, text=c).pack(side="left", padx=5)
            self.approach_coords.append(ctk.CTkEntry(self.frame3, width=65))
            self.approach_coords[-1].insert(0, f"{self.config['default_coords']['approach_point'][c]}")
            self.approach_coords[-1].pack(side="left", padx=10)
        
        self.frame4 = ctk.CTkFrame(self)
        self.frame4.pack(pady=25)
        
        ctk.CTkLabel(self.frame4, text="Offsets de dégagement").pack()
        
        self.clearance_coords = []
        for c in ["x_offset", "y_offset", "z_offset"]:
            ctk.CTkLabel(self.frame4, text=c).pack(side="left", padx=5)
            self.clearance_coords.append(ctk.CTkEntry(self.frame4, width=65))
            self.clearance_coords[-1].insert(0, f"{self.config['default_coords']['clearance_point'][c]}")
            self.clearance_coords[-1].pack(side="left", padx=10)
        
        ctk.CTkButton(self, text="Sauvegarder", command=self.save).pack()

    def save(self):
        try:
            int(self.port_entry.get())
        except:
            messagebox.showerror(
                title="Erreur", 
                icon="error", 
                message=f"Port invalide : {self.port_entry.get()}"
            )
            return
        
        for i, c in enumerate(["x", "y", "z", "a", "b", "c"]):
            try:
                float(self.origin_coords[i])
            except:
                messagebox.showerror(
                    title="Erreur", 
                    icon="error", 
                    message=f"Coordonée origine invalide pour {c} : {self.origin_coords[i]}"
                )
                return
        
        for i, c in enumerate(["x_offset", "y_offset", "z_offset"]):
            try:
                float(self.approach_coords[i])
            except:
                messagebox.showerror(
                    title="Erreur", 
                    icon="error", 
                    message=f"Offset d'approche invalide pour {c} : {self.approach_coords[i]}"
                )
                return

        for i, c in enumerate(["x_offset", "y_offset", "z_offset"]):
            try:
                float(self.clearance_coords[i])
            except:
                messagebox.showerror(
                    title="Erreur", 
                    icon="error", 
                    message=f"Offset de dégagement invalide pour {c} : {self.clearance_coords[i]}"
                )
                return
        
        Password(self, self.password_callback).mainloop()

    def password_callback(self, res):
        if not res:
            return
        
        self.config["robot"]["ip"] = self.ip_entry.get()
        self.config["robot"]["port"] = float(self.port_entry.get())
        
        for i, c in enumerate(["x", "y", "z", "a", "b", "c"]):
            self.config['default_coords']['origin'][c] = float(self.origin_coords[i].get())
        
        for i, c in enumerate(["x_offset", "y_offset", "z_offset"]):
            self.config['default_coords']['approach_point'][c] = float(self.approach_coords[i].get())
            self.config['default_coords']['clearance_point'][c] = float(self.clearance_coords[i].get())
        
        with open(resource_path("config.json"), "w") as f:
            json.dump(self.config, f, indent=4)