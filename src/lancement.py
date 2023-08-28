import customtkinter as ctk
from trajectory_lib import Trajectory, Movement
import time
from tcp_ip_advance.computer import TCPClient
import threading
from tkinter import TclError

class Run(ctk.CTkToplevel):
    def __init__(self, master, robot, trajectory, pieces_amount=-1, callback=lambda: 0):
        super().__init__()
        self.title("Ajouter un élément")
        self.geometry("850x700")
        
        self.robot: TCPClient = robot
        self.callback = callback
        
        self.trajectory: Trajectory = trajectory
        self.pieces_amount = pieces_amount
        
        self.label3 = ctk.CTkLabel(self, text="Lancement", font=("Arial", 20))
        self.label3.pack(pady=10)
        
        self.label4 = ctk.CTkLabel(self, text=f"Trajectoire choisie : {self.trajectory.name}", font=("Arial", 14))
        self.label4.pack(pady=5)
        
        if pieces_amount == -1:
            self.label5 = ctk.CTkLabel(self, text="Choisissez le nombre de pièces à produire", font=("Arial", 14))
            self.label5.pack(pady=5)

            self.amount_entry = ctk.CTkEntry(self)
            self.amount_entry.pack(pady=10)
        
        self.button2 = ctk.CTkButton(self, text="Lancer", command=self.run_btn)
        self.button2.pack(pady=20)
        
        self.label6 = ctk.CTkLabel(self, text="Avancement", font=("Arial", 14))
        self.label6.pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self, state='disabled', height=200, font=("Arial", 14))
        self.textbox.pack(padx=5, fill="both", expand=True)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def run_btn(self):
        self.stop_thread_flag = False
        self.start_thread()

    def on_closing(self):
        self.callback()
        self.stop_thread_flag = True
        self.after(1000, self.destroy())
    
    def start_thread(self):
        self.stop_thread_flag = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.check_thread()
    
    def check_thread(self):
        if self.thread.is_alive():
            self.after(250, self.check_thread)
        else:
            self.thread.join()
    
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
            try:
                self.pieces_amount = int(self.amount_entry.get())
            except:
                self.add_text("Erreur : Le nombre de pièce doit être un nombre entier")
        
        self.add_text(f"Trajectoire : {'test' if self.trajectory.name == '' else self.trajectory.name}")
        self.add_text(f"Pièces à produire : {self.pieces_amount}")
        self.add_text(f"{'-'*20}\n")

        translations = {
            Movement.START: "Début",
            Movement.LINEAR: "Linéaire",
            Movement.CIRCULAR: "Circulaire",
            Movement.PASS: "Passage"
        }
        
        times = []
        for i in range(self.pieces_amount):
            self.add_text(f"-> Pièce {i + 1}/{self.pieces_amount}\n")
            landmark = time.time()

            for i, m in enumerate(self.trajectory.trajectory):
                if self.stop_thread_flag:
                    return
                self.add_text(f"[{i+1}/{self.pieces_amount + 1}] Lancement de \"{translations[m.nature]}, {m.config}, cordon={m.wield_width}, {m.str_coords_pos()}\" :", end=" ")
                try:
                    match m.nature:
                        case Movement.START:
                            if not self.robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_NONE", "DR_BASE", "DR_MV_MOD_ABS"):
                                self.add_text(f"Erreur")
                                return
                        case Movement.LINEAR:
                            if not self.robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_WELD", "DR_BASE", "DR_MV_MOD_ABS"):
                                self.add_text(f"Erreur")
                                return
                        case Movement.CIRCULAR:
                            if self.robot.gotoc(m.coords[0].get_as_array(), m.coords[1].get_as_array(), m.vel, m.acc, "DR_MV_APP_WELD", "DR_BASE", "DR_MV_MOD_ABS"):
                                self.add_text(f"Erreur")
                                return
                        case Movement.PASS:
                            if not self.robot.gotop(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_BASE", "DR_MV_MOD_ABS"):
                                self.add_text(f"Erreur")
                                return
                except Exception as ex:
                    self.add_text(f"Erreur : {ex}")
                    return
                self.add_text("Ok")
            
            if self.stop_thread_flag:
                    return
             
            self.add_text(f"[{self.pieces_amount + 1}/{self.pieces_amount + 1}] Lancement de \"Point de dégagement\" : ", end=" ")
            try:
                self.robot.gotooffset(-50, 30, 20, "DR_TOOL", "DR_MV_MOD_REL")
            except Exception as ex:
                self.add_text(f"Erreur : {ex}")
                return
            self.add_text("Ok\n")
            
            times.append(time.time() - landmark)
            self.add_text(f"Pièce réalisée en {self.time_display(times[-1])}")
            if i + 1 != self.pieces_amount:
                estimated_time = (self.pieces_amount - (i + 1)) * sum(times) / len(times)
                self.add_text(f"Temps restant {self.time_display(estimated_time)}")
            self.add_text(f"")

        self.add_text(f"{'-'*20}")
        self.add_text(f"Execution terminée en {self.time_display(sum(times))}")

    def _is_window_alive(self):
        try:
            self.winfo_exists()
            return True
        except TclError:
            return False