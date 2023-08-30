import customtkinter as ctk

ctk.set_default_color_theme("Office_Like.json")
ctk.set_appearance_mode("light")

root = ctk.CTk()
root.geometry("450x350")

combo = ctk.CTkComboBox(root, values=["Item 1", "Item 2", "Item 3"])
combo.pack()

root.mainloop()