import customtkinter as ctk
from CTkListbox import CTkListbox
from tkinter import messagebox
from lancement import Run
from trajectory_lib import Trajectory, Movement, Coordinate
import time
import threading
from tkinter import TclError
from tcp_ip_advance.computer import TCPClient
from path_changer import resource_path
from window_tools import center_right_window

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

class NewTrajectory(ctk.CTkToplevel):
    def __init__(self, master, robot, callback, directory):
        super().__init__()
        
        self.grab_set()
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        self.title("Ajouter un élément")
        center_right_window(self, 650, 850)

        self.robot: TCPClient = robot
        self.callback = callback

        self.trajectory: Trajectory = Trajectory("")
        self.directory = directory

        font = ctk.CTkFont("Arial", 20, weight="bold")
        ctk.CTkLabel(self, text="NOUVELLE TRAJECTOIRE", font=font, text_color="#327DFF").pack(pady=10)
        
        ctk.CTkLabel(self, text="1 - Suivez les instructions pour ajouter des mouvements").pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self, state='disabled', height=200)
        self.textbox.pack(padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(self, text="Mouvements").pack(pady=5)

        self.listbox = CTkListbox(self, command=self.on_list_click)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_listbox()

        ctk.CTkLabel(self, text="2 - Testez la trajectoire").pack(pady=5)
        self.button1 = ctk.CTkButton(self, text="Test", command=self.test_trajectory)
        self.button1.pack(pady=10)

        ctk.CTkLabel(self, text="3 - Si la trajectoire est correcte, sauvegardez").pack(pady=5)
        self.button2 = ctk.CTkButton(self, text="Sauvegarder", command=self.save_trajectory)
        self.button2.pack(pady=10)
        
        self.stop_thread_flag = False
        self.start_thread()

    def refresh_listbox(self):
        self.listbox.delete("all")
        for m in self.trajectory.trajectory:
            self.listbox.insert("END", f"{Movement.TRANSLATIONS[m.nature]}, {m.config}, {m.str_coords_pos()}")

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
        self.stop_thread_flag = False
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
        
        ACTUALIZATION_TIME = 0.1
        
        self.add_text("- Pour enregistrer une nouvelle trajectoire, appuyez sur le bouton vert")
        while not self.robot.get_digital_input(1) and not self.stop_thread_flag and self._is_window_alive():
            time.sleep(ACTUALIZATION_TIME)

        i = 0
        while not self.stop_thread_flag and self._is_window_alive():
            nature_choice = 0
            self.add_text(f"\n- Pour ajouter un mouvement, choisissez un type. (vert = Linéaire, bleu1 = Circulaire{'' if i == 0 else ', bleu2 = Passage'})")
            while not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)
                
                if self.robot.get_digital_input(1):
                    nature_choice = Movement.LINEAR
                    break
                elif self.robot.get_digital_input(2):
                    nature_choice = Movement.CIRCULAR
                    break
                elif i != 0 and self.robot.get_digital_input(3):
                    nature_choice = Movement.PASS
                    break
            
            if self.stop_thread_flag or not self._is_window_alive():
                break
            
            while self.robot.get_digital_input(1) or self.robot.get_digital_input(2) or self.robot.get_digital_input(3):
                pass
            
            self.add_text(f"Choix : {Movement.TRANSLATIONS[nature_choice]}")

            self.add_text("- Placer la machine au point voulu puis appuyez sur le bouton vert.")
            self.robot.wait_manual_guide()
            while not self.robot.get_digital_input(1) and not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)
                
            if self.stop_thread_flag or not self._is_window_alive():
                break
            while self.robot.get_digital_input(1):
                pass

            point1 = Coordinate(*self.robot.get_current_posx()[0])
            self.add_text(f"Coordonées du point : {point1.str_pos()}")

            if nature_choice == Movement.CIRCULAR and i != 0:
                self.add_text("- Placer la machine au deuxième point voulu puis appuyez sur le bouton vert.")
                self.robot.wait_manual_guide()
                while not self.robot.get_digital_input(1) and not self.stop_thread_flag and self._is_window_alive():
                    time.sleep(ACTUALIZATION_TIME)
                    
                if self.stop_thread_flag or not self._is_window_alive():
                    break
                while self.robot.get_digital_input(1):
                    pass
                point2 = Coordinate(*self.robot.get_current_posx()[0])
                self.add_text(f"Coordonées du deuxième point : {point2.str_pos()}")
            
            configuration_choice = 0
            self.add_text("- Choisissez une configuration (vert = PA, bleu1 = PB)")
            while not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)

                if self.robot.get_digital_input(1):
                    configuration_choice = "PA"
                    break
                elif self.robot.get_digital_input(2):
                    configuration_choice = "PB"
                    break
            
            if self.stop_thread_flag or not self._is_window_alive():
                break
            while self.robot.get_digital_input(1) or self.robot.get_digital_input(2):
                pass
            
            if nature_choice != Movement.PASS:
                wield_width_available = [0, 3, 4, 5, 6, 8, 6, 8, 10, 12]
                while True:
                    wield_width = ctk.CTkInputDialog(text=f"Entrez la taille du cordon {wield_width_available}", title="Taille du cordon").get_input()
                    try:
                        wield_width = int(wield_width)
                        assert wield_width in wield_width_available
                        break
                    except:
                        self.add_text(f"Taille de cordon invalide : {wield_width}")
            else:
                wield_width = 0

            if nature_choice == Movement.CIRCULAR:
                self.add_text(f"Mouvement créé : {Movement.TRANSLATIONS[nature_choice]}, {configuration_choice}, cordon={wield_width}, {point1.str_pos()}, {point2.str_pos()}")
            elif nature_choice == Movement.PASS:
                self.add_text(f"Mouvement créé : {Movement.TRANSLATIONS[nature_choice]}, {configuration_choice}, {point1.str_pos()}")
            else:
                self.add_text(f"Mouvement créé : {Movement.TRANSLATIONS[nature_choice]}, {configuration_choice}, cordon={wield_width}, {point1.str_pos()}")

            confirm_choice = False
            self.add_text(f"Est-ce que le mouvement vous convient ? (vert = oui, bleu1 = non)", end=" ")
            while not self.stop_thread_flag and self._is_window_alive():
                time.sleep(ACTUALIZATION_TIME)

                if self.robot.get_digital_input(1):
                    confirm_choice = True
                    break
                elif self.robot.get_digital_input(2):
                    confirm_choice = False
                    break
            
            if self.stop_thread_flag or not self._is_window_alive():
                break
            while self.robot.get_digital_input(1) or self.robot.get_digital_input(2):
                pass

            if not confirm_choice:
                continue

            configuration = {"PA": Movement.PA, "PB": Movement.PB}[configuration_choice]
            
            if nature_choice == Movement.CIRCULAR:
                self.trajectory.add_movement(self.robot, Movement(nature_choice, configuration, wield_width, [point1, point2]))
            else:
                self.trajectory.add_movement(self.robot, Movement(nature_choice, configuration, wield_width, [point1]))
            
            self.refresh_listbox()
            self.add_text(f"Enregistré")
            
            i += 1

    def kill_thread(self):
        self.thread.join()

    def on_closing(self):
        self.callback()
        self.stop_thread_flag = True
        self.after(1000, self.kill_thread)
        self.after(1500, self.destroy())

    def check_thread(self):
        if self.thread.is_alive():
            self.after(100, self.check_thread)
        else:
            self.kill_thread()

    def on_list_click(self, _):
        pass

    def test_trajectory(self):
        self.stop_thread_flag = True
        time.sleep(1)
        run_window = Run(self, self.robot, self.trajectory, 1, self.save_trajectory)
        run_window.mainloop()

    def save_trajectory(self):
        def validate_entry():
            self.trajectory.name = name_entry.get()
            if self.trajectory.save(self.directory):
                popup.destroy()
                self.on_closing()
            else:
                return

        popup = ctk.CTkToplevel(self)
        popup.grab_set()
        center_right_window(popup, 350, 150)
        popup.title("Sauvegarde")

        label = ctk.CTkLabel(popup, text="Entrez le nom de la trajectoire")
        label.pack(pady=10)

        name_entry = ctk.CTkEntry(popup)
        name_entry.pack(pady=10, padx=10, fill="x")

        self.frame = ctk.CTkFrame(popup)
        self.frame.pack()

        validate_button = ctk.CTkButton(self.frame, text="Sauvegarder", command=validate_entry)
        validate_button.pack(side="left", padx=10, pady=5)
        delete_button = ctk.CTkButton(self.frame, text="Supprimer", command=lambda: self.confirm_cancel(popup))
        delete_button.pack(side="left", pady=5)

    def confirm_cancel(self, popup):
        if messagebox.askyesno(
            title="Confirmation", 
            icon="warning", 
            message="Êtes-vous sûr de ne pas vouloir conserver la trajectoire créée ?"
        ):
            popup.destroy()
            self.on_closing()
    
    def _is_window_alive(self):
        try:
            self.winfo_exists()
            return True
        except TclError:
            return False