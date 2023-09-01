import customtkinter as ctk
from path_changer import resource_path
from window_tools import center_right_window

class Password(ctk.CTkToplevel):   
    def __init__(self, master, callback):
        super().__init__(master)
        
        self.callback = callback
        
        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        center_right_window(self, 300, 160)
        self.title("Mot de passe")
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="MOT DE PASSE", font=font, text_color="#327DFF").pack(pady=10)
        
        self.entry = ctk.CTkEntry(self, show="*")
        self.entry.pack(pady=5)
    
        self.button = ctk.CTkButton(self, text="Ok", command=self.check_password)
        self.button.pack(pady=10)
        
        self.result = ctk.CTkLabel(self, text="")
        self.result.pack(pady=5)
    
    def check_password(self):
        if self.entry.get() != "admin":
            self.result.configure(text="Mot de passe invalide")
            return

        self.callback(True)
        self.after(250, self.destroy())