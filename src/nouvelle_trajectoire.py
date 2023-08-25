import customtkinter as ctk
from CTkListbox import CTkListbox
from tkinter import messagebox
from lancement import Run
from trajectory_lib import Trajectory, Movement, Coordinate
import time
import threading
from tkinter import TclError
from tcp_ip_advance.computer import TCPClient

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

class NewTrajectory(ctk.CTk):
    def __init__(self, master, directory):
        super().__init__()
        self.title("Ajouter un élément")
        self.center_window(700, 850)

        self.trajectory: Trajectory = Trajectory("")
        self.directory = directory

        self.title_label = ctk.CTkLabel(self, text="Nouvelle Trajectoire", font=("Arial", 20))
        self.title_label.pack(pady=10)
        
        self.label3 = ctk.CTkLabel(self, text="1 - Suivez les instructions", font=("Arial", 14))
        self.label3.pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self, state='disabled', height=200, font=("Arial", 14))
        self.textbox.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.label2 = ctk.CTkLabel(self, text="Mouvements", font=("Arial", 14))
        self.label2.pack(pady=5)

        self.listbox = CTkListbox(self, command=self.on_list_click, height=75)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_listbox()

        self.label4 = ctk.CTkLabel(self, text="3 - Testez la trajectoire", font=("Arial", 14))
        self.label4.pack(pady=5)
        self.button1 = ctk.CTkButton(self, text="Test", command=self.test_trajectory)
        self.button1.pack(pady=10)

        self.label5 = ctk.CTkLabel(self, text="4 - Si la trajectoire est correcte, sauvegardez", font=("Arial", 14))
        self.label5.pack(pady=5)
        self.button2 = ctk.CTkButton(self, text="Sauvegarder", command=self.save_trajectory)
        self.button2.pack(pady=10)
        
        self.stop_thread_flag = False
        self.start_thread()

    def refresh_listbox(self):
        self.listbox.delete("all")
        translations = {"START": "Début", "LINEAR": "Linéaire", "CIRCULAR": "Circulaire", "PASS": "Passage"}
        for m in self.trajectory.trajectory:
            self.listbox.insert("END", f"{translations[m.nature]}, {m.config}, {m.str_coords_pos()}")

    def center_window(self, width=None, height=None):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if width is None:
            width = self.winfo_width()
        if height is None:
            height = self.winfo_height()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def start_thread(self):
        self.thread = threading.Thread(target=self.start_taking_movements)
        self.thread.start()
        self.check_thread()
    
    def add_text(self, text, end="\n"):
        self.textbox.configure(state='normal')
        self.textbox.insert("end", f"{text}{end}")
        self.textbox.configure(state='disabled')
        self.textbox.see("end")

    def start_taking_movements(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', "end")
        self.textbox.configure(state='disabled')
        
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
        
        ACTUALIZATION_TIME = 0.25
        
        self.add_text("- Pour enregistrer une nouvelle trajectoire, appuyez sur le bouton vert")
        while not robot.get_digital_input(1) and not self.stop_thread_flag and self._is_window_alive():
            time.sleep(ACTUALIZATION_TIME)

        while not self.stop_thread_flag and self._is_window_alive():
            nature_choice = 0
            self.add_text("\n- Pour ajouter un mouvement, choisissez un type. (vert = Linéaire, bleu1 = Circulaire, bleu2 = Passage)")
            while not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)
                
                if robot.get_digital_input(1):
                    nature_choice = "Linéaire"
                    break
                elif robot.get_digital_input(2):
                    nature_choice = "Circulaire"
                    break
                elif robot.get_digital_input(3):
                    nature_choice = "Passage"
                    break
            
            while robot.get_digital_input(1) or robot.get_digital_input(2) or robot.get_digital_input(3):
                pass
            
            self.add_text(f"Choix : {nature_choice}")


            self.add_text("- Placer la machine au point voulu puis appuyez sur le bouton vert.")
            robot.wait_manual_guide()
            while not robot.get_digital_input(1) and not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)
            while robot.get_digital_input(1):
                pass

            point1 = Coordinate(*robot.get_current_posx()[0])
            self.add_text(f"Coordonées du point : {point1.str_pos()}")

            if nature_choice == "Circulaire":
                self.add_text("- Placer la machine au deuxième point voulu puis appuyez sur le bouton vert.")
                robot.wait_manual_guide()
                while not robot.get_digital_input(1) and not self.stop_thread_flag and self._is_window_alive():
                    time.sleep(ACTUALIZATION_TIME)
                while robot.get_digital_input(1):
                    pass
                point2 = Coordinate(*robot.get_current_posx()[0])
                self.add_text(f"Coordonées du deuxième point : {point2.str_pos()}")
            
            configuration_choice = 0
            self.add_text("- Choisissez une configuration (vert = PA, bleu1 = PB)")
            while not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)

                if robot.get_digital_input(1):
                    configuration_choice = "PA"
                    break
                elif robot.get_digital_input(2):
                    configuration_choice = "PB"
                    break

            wield_width = 0
            
            while robot.get_digital_input(1) or robot.get_digital_input(2):
                pass
            
            if nature_choice == "Circulaire":
                self.add_text(f"Mouvement créé : {nature_choice}, {configuration_choice}, cordon={wield_width}, {point1.str_pos()}, {point2.str_pos()}")
            else:
                self.add_text(f"Mouvement créé : {nature_choice}, {configuration_choice}, cordon={wield_width}, {point1.str_pos()}")

            confirm_choice = False
            self.add_text(f"Est-ce que le mouvement vous convient ? (vert = oui, bleu1 = non)", end=" ")
            while not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)

                if robot.get_digital_input(1):
                    confirm_choice = True
                    break
                elif robot.get_digital_input(2):
                    confirm_choice = False
                    break
            
            while robot.get_digital_input(1) or robot.get_digital_input(2):
                pass

            if not confirm_choice:
                continue
                
            nature = {"Linéaire": Movement.LINEAR, "Circulaire": Movement.CIRCULAR, "Passage": Movement.PASS}[nature_choice]
            configuration = {"PA": Movement.PA, "PB": Movement.PB}[configuration_choice]
            
            if nature == Movement.CIRCULAR:
                self.trajectory.add_movement(Movement(nature, configuration, wield_width, [point1, point2]))
            else:
                self.trajectory.add_movement(Movement(nature, configuration, wield_width, [point1]))
            
            self.trajectory.compile()
            
            self.refresh_listbox()
            
            self.add_text(f"Enregistré")

    def kill_thread(self):
        self.thread.join()
        self.destroy()

    def on_closing(self):
        self.stop_thread_flag = True
        self.after(1000, self.kill_thread)
    
    def check_thread(self):
        if self.thread.is_alive():
            self.after(100, self.check_thread)
        else:
            self.destroy()
            

    def on_list_click(self, _):
        pass

    def test_trajectory(self):
        run_window = Run(self, self.trajectory)
        run_window.mainloop()
        pass

    def save_trajectory(self):
        def validate_entry():
            self.trajectory.name = name_entry.get()
            if self.trajectory.save(self.directory):
                popup.destroy()
            else:
                return

        popup = ctk.CTkToplevel(self)
        popup.geometry("350x150")
        popup.title("Nom Trajectoire")

        label = ctk.CTkLabel(popup, text="Choisissez le nom de la trajectoire")
        label.pack(pady=10)

        name_entry = ctk.CTkEntry(popup)
        name_entry.pack(pady=10, padx=10, fill="x")

        validate_button = ctk.CTkButton(popup, text="Valider", command=validate_entry)
        validate_button.pack(pady=10)

    def on_button3_click(self):
        response = messagebox.askyesno(
            title="Confirmation", 
            icon="warning", 
            message="Êtes-vous sûr de vouloir supprimer la trajectoire ?"
        )
        if response:
            pass
    
    def _is_window_alive(self):
        try:
            self.winfo_exists()
            return True
        except TclError:
            return False