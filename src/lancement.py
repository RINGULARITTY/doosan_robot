import customtkinter as ctk
from trajectory_lib import Trajectory, Movement
import time
from tcp_ip_advance.computer import TCPClient
import threading
from tkinter import TclError
from path_changer import resource_path
from window_tools import center_right_window
from material_builder import Materials
from key_gen import KeyGen

class Run(ctk.CTkToplevel):
    def __init__(self, master, robot, trajectory, pieces_amount=1, callback=lambda: 0):
        super().__init__(master)
        
        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        
        self.title("Production")
        center_right_window(self, 650, 775)
        
        self.robot: TCPClient = robot
        self.callback = callback
        
        self.trajectory: Trajectory = trajectory
        self.pieces_amount = pieces_amount
        
        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="LANCEMENT", font=font, text_color="#327DFF").pack(pady=10)

        ctk.CTkLabel(self, text=f"Trajectoire choisie : {self.trajectory.name}", font=("Arial", 18)).pack(pady=5)
        ctk.CTkLabel(self, text="Choisissez le nombre de pièces à produire").pack(pady=5)

        self.amount_entry = ctk.CTkEntry(self)
        self.amount_entry.pack(pady=10)
        self.amount_entry.configure(textvariable=f"{pieces_amount}")
        
        self.materials = Materials()
        self.key = KeyGen.get_default_key()
        material_choices = []
        if self.key == None:
            ctk.CTkLabel(self, text="Clef de déchiffrement manquante", font=("Arial", 12)).pack(pady=5)
        else:
            self.materials.load(self.key)
            materials_names = [Materials.TRANSLATIONS[m] for m in self.materials.get_materials_names() ]
            if len(materials_names) == 0:
                ctk.CTkLabel(self, text="Materiaux manquants", font=("Arial", 12)).pack(pady=5)
            material_choices = material_choices + materials_names
        
        ctk.CTkLabel(self, text="Choisissez un matériaux").pack(pady=5)
        material_choices = [Materials.NO_WIELD] + material_choices
        self.material_choice = ctk.CTkComboBox(self, values=material_choices, width=400)
        self.material_choice.pack(pady=10)
        self.material_choice.set("Sans soudure")
        
        self.start_btn = ctk.CTkButton(self, text="Lancer", command=self.run_btn)
        self.start_btn.pack(pady=15)
        
        ctk.CTkLabel(self, text="Avancement", font=("Arial", 16)).pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self, state='disabled')
        self.textbox.pack(padx=5, fill="both", expand=True)
        
        self.stop_btn = ctk.CTkButton(self, text="Arrêt", command=self.cancel_btn)
        self.stop_btn.pack(pady=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run_btn(self):
        self.stop_thread_flag = False
        self.start_thread()
    
    def cancel_btn(self):
        self.stop_thread_flag = True

    def on_closing(self):
        self.stop_thread_flag = True
        time.sleep(0.5)
        self.callback()
        self.after(500, self.destroy())
    
    def start_thread(self):
        self.stop_thread_flag = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.check_thread()
    
    def check_thread(self):
        if self.thread.is_alive() and not self.stop_thread_flag:
            self.after(250, self.check_thread)
        else:
            self.thread.join()
    
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

        try:
            self.pieces_amount = int(self.amount_entry.get())
            assert self.pieces_amount > 0
        except:
            self.add_text("Erreur : Le nombre de pièce doit être un nombre entier >= 1")
            self.stop_thread_flag = True
            return
            
        
        self.add_text("Assurez vous que le robot est dégagé de la pièce")
        self.robot.wait_manual_guide()
        
        self.add_text(f"\nTrajectoire : {'test' if self.trajectory.name == '' else self.trajectory.name}")
        self.add_text(f"Pièces à produire : {self.pieces_amount}")
        self.add_text(f"Materiau : {self.material_choice.get()}")
        self.add_text(f"{'-'*20}\n")
        
        wield = Materials.NO_WIELD if self.material_choice.get() == Materials.NO_WIELD else {v: k for k, v in Materials.TRANSLATIONS.items()}[self.material_choice.get()]
        if wield != "Sans Soudure":
            material = self.materials.get_material_from_name(wield)
        
        ACTIONS = {
            Movement.ORIGIN: lambda m: self.robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_NONE", "DR_BASE", "DR_MV_MOD_ABS"),
            Movement.APPROACH_POINT: lambda m: self.robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_NONE", "DR_BASE", "DR_MV_MOD_ABS"),
            Movement.CLEARANCE: lambda m: self.robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_NONE", "DR_BASE", "DR_MV_MOD_ABS"),
            Movement.LINEAR: lambda m: self.robot.goto(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_MV_APP_WELD", "DR_BASE", "DR_MV_MOD_ABS"),
            Movement.CIRCULAR: lambda m: self.robot.gotoc(m.coords[0].get_as_array(), m.coords[1].get_as_array(), m.vel, m.acc, "DR_MV_APP_WELD", "DR_BASE", "DR_MV_MOD_ABS"),
            Movement.PASS: lambda m: self.robot.gotop(*m.coords[0].get_as_array(), m.vel, m.acc, "DR_BASE", "DR_MV_MOD_ABS")
        }
        
        times = []
        for i in range(self.pieces_amount):
            self.add_text(f"-> Pièce {i + 1}/{self.pieces_amount}\n")
            landmark = time.time()

            for j, m in enumerate(self.trajectory.trajectory):
                if self.stop_thread_flag:
                    self.add_text("Arrêt forcé")
                    return

                self.add_text(f"[{j+1}/{len(self.trajectory.trajectory)}] Lancement de \"{Movement.TRANSLATIONS[m.nature]}, {m.config}, cordon={m.wield_width}, {m.str_coords_pos()}\" :", end=" ")

                try:
                    if wield != Materials.NO_WIELD and m.wield_width > 0:
                        self.add_text("Soudage activé", end=" ")
                        self.robot.start_wield(
                            material.loc[material['bead_widths'] == m.wield_width, 'robot_speed'].iloc[0],
                            material.loc[material['bead_widths'] == m.wield_width, 'job'].iloc[0],
                            material.loc[material['bead_widths'] == m.wield_width, 'synergic_id'].iloc[0],
                        )
                    res = ACTIONS[m.nature](m)
                    if not res[0]:
                        self.add_text(f"Erreur machine : {res[1]}")
                        self.stop_thread_flag = True
                        return
                    self.add_text("Mouvement Ok", end=" ")
                    if wield != Materials.NO_WIELD and m.wield_width > 0:
                        self.add_text("Soudage désactivé", end=" ")
                        self.robot.end_wield()
                    else:
                        self.add_text(" ")
                except Exception as ex:
                    self.add_text(f"Erreur : {ex}")
                    return
            
            self.add_text("")
            
            if self.stop_thread_flag:
                self.add_text("Arrêt forcé")
                return
            
            times.append(time.time() - landmark)
            self.add_text(f"Pièce réalisée en {self.time_display(times[-1])}", end="")
            if i + 1 != self.pieces_amount:
                estimated_time = (self.pieces_amount - (i + 1)) * sum(times) / len(times)
                self.add_text(f", temps restant {self.time_display(estimated_time)}")
                self.add_text(f"Placez la nouvelle pièce et appuyez sur le bouton vert pour continuer")
                while not self.stop_thread_flag and not self.robot.get_digital_input(1):
                    time.sleep(0.25)
            else:
                self.add_text("")

        self.add_text(f"{'-'*20}")
        self.add_text(f"Execution terminée en {self.time_display(sum(times))}")

    def _is_window_alive(self):
        try:
            self.winfo_exists()
            return True
        except TclError:
            return False