import customtkinter as ctk

def open_child():
    child_window = ctk.CTkToplevel(root)
    child_window.grab_set()
    ctk.CTkLabel(child_window, text="Je suis une fenêtre enfant").pack()
    ctk.CTkButton(child_window, text="Fermer", command=child_window.destroy).pack()

root = ctk.CTk()
root.title("Fenêtre parent")

ctk.CTkLabel(root, text="Je suis la fenêtre parent").pack()
ctk.CTkButton(root, text="Ouvrir fenêtre enfant", command=open_child).pack()
ctk.CTkButton(root, text="Issou", command=lambda : print("issou")).pack()

root.mainloop()