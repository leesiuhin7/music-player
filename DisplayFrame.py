import tkinter as tk
from typing import Any

class DisplayFrame:
                
    def __init__(self,
                 master: tk.Frame | tk.Canvas,
                 input_data: list[Any],
                 display_id: int,
                 colour_theme: dict[str, str]) -> None:

        self.master = master
        self.colour_theme = colour_theme

        self.id = display_id
        self.input_data = input_data


        self.frame = tk.Frame(
            self.master,
            bg=self.colour_theme["bg"])

        self.frame.bind("<Enter>", self.enter_func)
        self.frame.bind("<Leave>", self.leave_func)
        
        self.name_lbl = tk.Label(
            self.frame,
            text="",
            anchor="w",
            bg=self.colour_theme["bg"],
            fg=self.colour_theme["fg"],
            padx=20)
        

    def load_widgets(self) -> None:
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, minsize=30)

        self.name_lbl.grid(column=1, row=0, 
                           sticky="nesw")


    def enter_func(self, event) -> None:        
        self.frame.config(bg=self.colour_theme["hover_bg"])
        self.name_lbl.config(bg=self.colour_theme["hover_bg"])


    def leave_func(self, event) -> None:
        self.frame.config(bg=self.colour_theme["bg"])
        self.name_lbl.config(bg=self.colour_theme["bg"])
            
        
    def update(self) -> None:
        if self.id < len(self.input_data):
            text = self.input_data[self.id]            
            self.name_lbl.config(text=text)

        else:
            self.name_lbl.config(text="")
            self.leave_func(None)
            return