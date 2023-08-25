import customtkinter as ctk
from trajectory_lib import Trajectory, Movement
import time
from tcp_ip_advance.computer import TCPClient

class Run(ctk.CTkToplevel):
    def __init__(self, master, trajectory, pieces_amount=-1, callback=lambda: 0):
        super().__init__()
        self.title("Ajouter un élément")
        self.geometry("450x700")
        
        self.callback = callback
        
        self.trajectory: Trajectory = trajectory
        self.pieces_amount = pieces_amount
        
        self.label3 = ctk.CTkLabel(self, text="Lancement", font=("Arial", 20))
        self.label3.pack(pady=10)
        
        self.label4 = ctk.CTkLabel(self, text=f"Trajectoire choisie : {self.trajectory.name}", font=("Arial", 14))
        self.label4.pack(pady=5)
        
        if pieces_amount != -1:
            self.label5 = ctk.CTkLabel(self, text="Choisissez le nombre de pièces à produire", font=("Arial", 14))
            self.label5.pack(pady=5)
        
            self.amount_entry = ctk.CTkEntry(self)
            self.amount_entry.pack(pady=10)
        
        self.button2 = ctk.CTkButton(self, text="Lancer", command=self.run)
        self.button2.pack(pady=20)
        
        self.label6 = ctk.CTkLabel(self, text="Avancement", font=("Arial", 14))
        self.label6.pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self, state='disabled', height=200, font=("Arial", 14))
        self.textbox.pack(padx=5, fill="both", expand=True)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.callback()
        self.after(250, self.destroy())
        
    def combobox_callback(self):
        pass
    
    def add_text(self, text, end="\n"):
        self.textbox.configure(state='normal')
        self.textbox.insert("end", f"{text}{end}")
        self.textbox.configure(state='disabled')
        self.textbox.see("end")
    
    def time_display(self, seconds):
        seconds = round(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"

        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = ((seconds % 3600) // 60) % 60
        return f"{h}h {m}m {s}s"
    
    def run(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', "end")
        self.textbox.configure(state='disabled')

        if self.pieces_amount == -1:
            self.pieces_amount = 1
        else:
            try:
                self.pieces_amount = int(self.amount_entry.get())
            except:
                self.add_text("Erreur : Le nombre de pièce doit être un nombre entier")
        
        self.add_text(f"Trajectoire : {self.trajectory.name}")
        self.add_text(f"Pièces à produire : {self.pieces_amount}")
        self.add_text(f"{'-'*20}\n")

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
        
        times = []
        for i in range(self.pieces_amount):
            self.add_text(f"-> Pièce {i + 1}/{self.pieces_amount}\n")
            landmark = time.time()

            for m in self.trajectory.trajectory:
                self.add_text(f"Lancement de \"{translations[m.nature]}, {m.config}, cordon={m.wield_width}, {m.str_coords_pos()}\" : ", end=" ")
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
                
            self.add_text(f"Lancement de \"Fin d'execution\" : ", end=" ")
            try:
                robot.gotooffset(-50, m.vel, m.acc, "DR_BASE", "DR_MV_MOD_ABS")
            except Exception as ex:
                self.add_text(f"Erreur : {ex}")
                robot.close_socket()
            self.add_text("Ok\n")
            
            times.append(time.time() - landmark)
            self.add_text(f"Pièce réalisée en {self.time_display(times[-1])}\n")
            if i != self.pieces_amount:
                estimated_time = (self.pieces_amount - (i + 1)) * sum(times) / len(times)
                self.add_text(f"Temps restant {self.time_display(estimated_time)}")
            self.add_text(f"{'-'*20}")

        self.add_text(f"Execution terminée en {self.time_display(sum(times))}")
