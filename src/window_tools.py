from customtkinter import CTk, CTkToplevel
from typing import Union

def center_right_window(window: Union[CTk, CTkToplevel], width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width = window.winfo_width()
    height = window.winfo_height()

    x = screen_width - width - 15
    y = (screen_height / 2) - (height / 2)
    
    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")