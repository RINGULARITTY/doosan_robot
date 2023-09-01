import customtkinter as ctk
from path_changer import resource_path
from window_tools import center_right_window
import json
from password import Password

class Settings(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        
        self.title("Paramètres")
        center_right_window(self, 650, 500)
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="PARAMETRES", font=font, text_color="#327DFF").pack(pady=10)
        
        with open(resource_path("config.json")) as f:
            config = json.load(f)
        
        self.frame1 = ctk.CTkFrame(self)
        self.frame1.pack(pady=10)
        
        ctk.CTkLabel(self.frame1, text="Connexion robot").pack()
        
        ctk.CTkLabel(self.frame1, text="Ip").pack(side="left", padx=5)
        self.ip_entry = ctk.CTkEntry(self.frame1)
        self.ip_entry.insert(0, config["robot"]["ip"])
        self.ip_entry.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.frame1, text="Port").pack(side="left", padx=5)
        self.port_entry = ctk.CTkEntry(self.frame1)
        self.port_entry.insert(0, f"{config['robot']['port']}")
        self.port_entry.pack(side="left", padx=10)
    
        self.frame2 = ctk.CTkFrame(self)
        self.frame2.pack(pady=10)
        
        ctk.CTkLabel(self.frame2, text="Coordonées origine").pack()

        self.origin_coords = []
        for c in ["x", "y", "z", "a", "b", "c"]:
            ctk.CTkLabel(self.frame2, text=c).pack(side="left", padx=5)
            self.origin_coords.append(ctk.CTkEntry(self.frame2, width=65))
            self.origin_coords[-1].insert(0, f"{config['default_coords']['origin'][c]}")
            self.origin_coords[-1].pack(side="left", padx=10)
        
        self.frame3 = ctk.CTkFrame(self)
        self.frame3.pack(pady=10)
        
        ctk.CTkLabel(self.frame3, text="Point d'approche").pack()
        
        self.approach_coords = []
        for c in ["x_offset", "y_offset", "z_offset"]:
            ctk.CTkLabel(self.frame3, text=c).pack(side="left", padx=5)
            self.approach_coords.append(ctk.CTkEntry(self.frame3, width=65))
            self.approach_coords[-1].insert(0, f"{config['default_coords']['approach_point'][c]}")
            self.approach_coords[-1].pack(side="left", padx=10)
        
        self.frame4 = ctk.CTkFrame(self)
        self.frame4.pack(pady=25)
        
        ctk.CTkLabel(self.frame4, text="Point de dégagement").pack()
        
        self.clearance_coords = []
        for c in ["x_offset", "y_offset", "z_offset"]:
            ctk.CTkLabel(self.frame4, text=c).pack(side="left", padx=5)
            self.clearance_coords.append(ctk.CTkEntry(self.frame4, width=65))
            self.clearance_coords[-1].insert(0, f"{config['default_coords']['clearance_point'][c]}")
            self.clearance_coords[-1].pack(side="left", padx=10)
        
        ctk.CTkButton(self, text="Sauvegarder", command=self.save).pack()

        ctk.CTkLabel(self, text="En cours de développement*").pack(side="left")

    def save(self):
        Password(self, self.password_callback).mainloop()

    def password_callback(self, res):
        if not res:
            return
        
        