import customtkinter as ctk
from CTkListbox import CTkListbox
from tkinter import messagebox
from lancement import Run
from trajectory_lib import Trajectory, Movement, Coordinate
import time
import threading
from tkinter import TclError
from machine import Machine

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

class NewTrajectory(ctk.CTk):
    def __init__(self, master):
        super().__init__()
        self.title("Ajouter un élément")
        self.center_window(700, 850)

        self.trajectory: Trajectory = Trajectory("")

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

        self.listbox.insert("END", f"Linéaire, (41.45, 68.74, -96.97), PB")

        self.label4 = ctk.CTkLabel(self, text="3 - Testez la trajectoire", font=("Arial", 14))
        self.label4.pack(pady=5)
        self.button1 = ctk.CTkButton(self, text="Test", command=self.on_button1_click)
        self.button1.pack(pady=10)

        self.label5 = ctk.CTkLabel(self, text="4 - Si la trajectoire est correcte, sauvegardez", font=("Arial", 14))
        self.label5.pack(pady=5)
        self.button2 = ctk.CTkButton(self, text="Sauvegarder", command=self.on_button2_click)
        self.button2.pack(pady=10)
        
        self.label5 = ctk.CTkLabel(self, text="Sinon, annulez", font=("Arial", 14))
        self.label5.pack(pady=5)
        self.button2 = ctk.CTkButton(self, text="Annuler", command=self.on_button3_click)
        self.button2.pack(pady=10)
        
        self.stop_thread_flag = False
        self.machine = Machine()
        self.start_thread()

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

    def start_taking_movements(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', "end")
        self.textbox.configure(state='disabled')
        
        while self.machine.get_digital_input(1) or not self.stop_thread_flag:
            self.add_text("- Pour enregistrer une nouvelle trajectoire, appuyez sur le bouton vert")
            while self.machine.get_digital_input(1) or not self.stop_thread_flag or not self._is_window_alive():
                time.sleep(2)
            
            nature_choice = 0
            self.add_text("- Pour ajouter un mouvement, choisissez un type. (vert = Linéaire, bleu1 = Circulaire, bleu2 = Passage)")
            while not self.stop_thread_flag or not self._is_window_alive():
                time.sleep(2)
                
                if self.machine.get_digital_input(1):
                    nature_choice = "Linéaire"
                    break
                elif self.machine.get_digital_input(2):
                    nature_choice = "Circulaire"
                    break
                elif self.machine.get_digital_input(3):
                    nature_choice = "Passage"
                    break
            
            self.add_text(f"Choix : {nature_choice}")

            self.add_text("- Placer la machine au point voulu puis appuyez sur le bouton vert.")
            while not self.stop_thread_flag or not self._is_window_alive() or not self.machine.get_digital_input(1):
                time.sleep(2)
            point1 = Coordinate(*self.machine.get_current_posx())
            self.add_text(f"Coordonées du point : {point1.str_pos()}")

            if nature_choice == "Circulaire":
                self.add_text("- Placer la machine au deuxième point voulu puis appuyez sur le bouton vert.")
                while not self.stop_thread_flag or not self._is_window_alive() or not self.machine.get_digital_input(1):
                    time.sleep(2)
                point2 = Coordinate(*self.machine.get_current_posx())
                self.add_text(f"Coordonées du deuxième point : {point2.str_pos()}")
            
            configuration_choice = 0
            self.add_text("- Choisissez une configuration (vert = PA, bleu = PB)")
            while not self.stop_thread_flag or not self._is_window_alive():
                time.sleep(2)

                if self.machine.get_digital_input(1):
                    movement_choice = "PA"
                    break
                elif self.machine.get_digital_input(2):
                    movement_choice = "PB"
                    break
            
            # Taille du cordon
            wield_width = 0
            
            if movement_choice == "Circulaire":
                self.add_text(f"Mouvement créé : {movement_choice}, {configuration_choice}, {point1}, {point2}")
            else:
                self.add_text(f"Mouvement créé : {movement_choice}, {configuration_choice}, {point1}")
            
            confirm_choice = False
            self.add_text(f"Est-ce que le mouvement vous convient ? (vert = oui, bleu = non)")
            while not self.stop_thread_flag or not self._is_window_alive():
                time.sleep(2)

                if self.machine.get_digital_input(1):
                    confirm_choice = False
                    break
                elif self.machine.get_digital_input(2):
                    confirm_choice = True
                    break
            
            if not confirm_choice:
                continue
                
            nature = {"Linéaire": Movement.LINEAR, "Circulaire": Movement.CIRCULAR, "Passage": Movement.PASS}[nature_choice]
            configuration = {"PA": Movement.PA, "PB": Movement.PB}
            
            if nature == Movement.CIRCULAR:
                self.trajectory.add_movement(Movement(nature, configuration, wield_width, [point1, point2]))
            else:
                self.trajectory.add_movement(Movement(nature, configuration, wield_width, [point1]))

    def add_text(self, text):
        self.textbox.configure(state='normal')
        self.textbox.insert("end", f"{text}\n")
        self.textbox.configure(state='disabled')
        self.textbox.see("end")

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

    def on_add2_click(self):
        
        pass

    def on_button1_click(self):
        run_window = Run(self)
        run_window.mainloop()
        pass

    def on_button2_click(self):
        def validate_entry():
            entered_name = name_entry.get()
            print(entered_name)
            popup.destroy()

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