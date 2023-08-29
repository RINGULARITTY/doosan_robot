import customtkinter as ctk
import time
from path_changer import resource_path

class Password(ctk.CTkToplevel):   
    def __init__(self, master, callback):
        super().__init__()
        
        self.callback = callback
        
        self.grab_set()
        self.after(250, self.iconbitmap(resource_path("./icon.ico")))
        
        self.title("Mot de passe")
        self.geometry("300x155")
        
        self.label = ctk.CTkLabel(self, text="Mot de Passe", font=("Arial", 20))
        self.label.pack(pady=10)
        
        self.entry = ctk.CTkEntry(self, show="*")
        self.entry.pack(pady=5)
    
        self.button = ctk.CTkButton(self, text="Ok", command=self.check_password)
        self.button.pack(pady=10)
        
        self.result = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.result.pack()
    
    def check_password(self):
        time.sleep(0.25)
        if self.entry.get() != "0":
            self.result.configure(text="Mot de passe invalide")
            return

        self.callback(True)
        self.after(250, self.destroy())