import customtkinter as ctk
from trajectory_lib import Trajectory, Movement
import time
from tcp_ip_advance.computer import TCPClient

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
    
    def add_text(self, text, end="\n"):
        self.textbox.configure(state='normal')
        self.textbox.insert("end", f"{text}{end}")
        self.textbox.configure(state='disabled')
        self.textbox.see("end")
    
    def run(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', "end")
        self.textbox.configure(state='disabled')

        translations = {
            Movement.START: "Début",
            Movement.LINEAR: "Linéaire",
            Movement.CIRCULAR: "Circulaire",
            Movement.PASS: "Passage"
        }

        ip, port = "192.168.127.100", 20002
        self.add_text(f"Connexion au robot {ip}:{port}...", end=" ")
        try:
            robot = TCPClient(ip, port)
        except Exception as ex:
            self.add_text(f"\nErreur : {ex}")
            return
        self.add_text(f"Ok")
        self.add_text(f"Dialogue avec le robot...", end=" ")
        response = robot.hi()
        if not response:
            self.add_text(f"\nErreur, réponse : {response}")
            return
        self.add_text(f"Ok\n")
        

        for m in self.trajectory.trajectory:
            self.add_text("end", f"Lancement de \"{translations[m.nature]}, {m.config}, cordon={m.wield_width}, {m.str_coords_pos()}\" : ", end=" ")
            try:
                match m.nature:
                    case Movement.START:
                        robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_NONE", "DR_BASE", "DR_MV_MOD_ABS")
                    case Movement.LINEAR:
                        robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_WELD", "DR_BASE", "DR_MV_MOD_ABS")
                    case Movement.CIRCULAR:
                        robot.gotoc(m.coords[0].get_as_array(), m.coords[1].get_as_array(), m.vel, m.acc, "DR_MV_APP_WELD", "DR_BASE", "DR_MV_MOD_ABS")
                    case Movement.PASS:
                        robot.gotop(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_BASE", "DR_MV_MOD_ABS")
            except Exception as ex:
                self.add_text("end", f"Erreur : {ex}")
                robot.close_socket()
            
            self.add_text("end", "Ok")
            
        self.add_text("end", f"Lancement de \"Fin d'execution\" : ", end=" ")
        try:
            robot.gotooffset(-50, m.vel, m.acc, "DR_BASE", "DR_MV_MOD_ABS")
        except Exception as ex:
            self.add_text("end", f"Erreur : {ex}")
            robot.close_socket()
        self.add_text("end", "Ok\n")
        
        self.add_text("end", "Execution terminée")
                    