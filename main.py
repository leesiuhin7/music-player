import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.font as tkfont
import os
from typing import Callable, Any, Type
from abc import ABC, abstractmethod

import _backend
from DisplayFrame import DisplayFrame



Backend = _backend.Backend()

self_path = _backend.self_path
img_path = os.path.join(self_path, "img")

colour_theme = {"bg": "#1f1f1f",
                "menu_bg": "#303030",
                "hover_bg": "#404040",
                "disabled_bg": "#7F7F7F",
                "scrollbar_bg": "#606060",
                "fg": "#ffffff",
                "scrollbar_fg": "#569CD6",
                "red": "#FF0000"}
   


class MainWindow:

    def __init__(self, 
                 size: tuple[int, int],
                 colour_theme: dict[str, str]) -> None:
        
        self.colour_theme = colour_theme

        self.root = tk.Tk()
        self.root.title("Music Player")

        w, h = size
        self.root.geometry(f"{w}x{h}")

        self.grid_frame = tk.Frame(self.root, bg=self.colour_theme["bg"])

        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_rowconfigure(0, weight=1)


        self._Menu = self.Menu(self)
        self._AudioPlayer = self.AudioPlayer(self)
        self._MainPanel = self.MainPanel(self)

        # menu objects

        self.menu_play_queue = self._Menu.MenuPlayQueue(
            self, self._Menu.frame)
        
        self.menu_library = self._Menu.MenuLibrary(
            self, self._Menu.frame)
        
        self.menu_playlist_top = self._Menu.PlaylistTop(
            self, self._Menu.frame)
        
        self.menu_playlists = self._Menu.Playlists(
            self, self._Menu.frame)
        
        self.new_playlist = self._Menu.NewPlaylist(
            self, self._Menu.frame)


    def init_window(self) -> None:
        self.grid_frame.place(x=0, y=0, relwidth=1, relheight=1)

        self._Menu.load_menu()


        # add play queue button to menu
        self._Menu.add_menu_item(
            self.menu_play_queue)
        
        # add music library button to menu
        self._Menu.add_menu_item(
            self.menu_library)
        

        self._Menu.add_menu_item(
            self.new_playlist)
        
        # add playlist button to menu
        self._Menu.add_menu_item(
            self.menu_playlist_top)
        
        # add playlist frame to menu
        self._Menu.add_menu_item(
            self.menu_playlists)
        

        self._AudioPlayer.load_audio_player()


    def update(self) -> None:
        Backend.update()
        self.root.update()
        self._AudioPlayer.update()
        self._MainPanel.update()
        self._Menu.update()


    def get_rel_pos(self, widget: tk.Widget) -> tuple[int, int]:
        x = widget.winfo_rootx() - self.root.winfo_rootx()
        y = widget.winfo_rooty() - self.root.winfo_rooty()

        return x, y



    class Menu: # the menu part of the window

        def __init__(self, MainWindow) -> None:

            self.colour_theme = MainWindow.colour_theme
            self.master = MainWindow.grid_frame
            self.frame = tk.Frame(self.master, 
                                  bg=self.colour_theme["menu_bg"], 
                                  width=200)
            self.frame.grid_propagate(False)
            self.frame.grid_columnconfigure(0, weight=1)

            self.menu_items = []
            self.menu_widgets: list[tk.Widget] = []

        
        class AbstractMenuItem(ABC):

            def __init__(self, 
                         MainWindow, 
                         master: tk.Misc) -> None:
                
                self.colour_theme = MainWindow.colour_theme
                self.MainWindow = MainWindow
                self.master = master

                self.widget = self.as_tk_widget()


            @abstractmethod
            def click_func(self, *args, **kwargs) -> None:
                pass


            def enter_func(self, event) -> None:
                self.widget.config(bg=self.colour_theme["hover_bg"])


            def leave_func(self, event) -> None:
                self.widget.config(bg=self.colour_theme["menu_bg"])

            
            @abstractmethod
            def as_tk_widget(self) -> Any:
                # return class object as a tk widget
                pass


            def update(self) -> None:
                pass
            

        class MenuPlayQueue(AbstractMenuItem):

            def __init__(self, 
                         MainWindow, 
                         master: tk.Misc) -> None:
                
                super().__init__(MainWindow, master)
                self.window = MainWindow._MainPanel.PlayQueueWin

            
            def click_func(self, event) -> None:
                self.MainWindow._MainPanel.set_active_frame(self.window)


            def as_tk_widget(self) -> tk.Label:
                widget = tk.Label(self.master, 
                                  text="Play Queue",
                                  bg=self.colour_theme["menu_bg"], 
                                  fg=self.colour_theme["fg"],
                                  anchor="w", 
                                  padx=10)
                
                widget.bind("<Button-1>", func=self.click_func)
                widget.bind("<Enter>", func=self.enter_func)
                widget.bind("<Leave>", func=self.leave_func)

                return widget
            


        class MenuLibrary(AbstractMenuItem):

            def __init__(self, 
                         MainWindow, 
                         master: tk.Misc) -> None:
                
                super().__init__(MainWindow, master)
                self.window = MainWindow._MainPanel.LibraryWin


            def click_func(self, event) -> None:
                self.MainWindow._MainPanel.set_active_frame(self.window)


            def as_tk_widget(self) -> tk.Label:
                widget = tk.Label(self.master,
                                  text="Music Library",
                                  bg=self.colour_theme["menu_bg"],
                                  fg=self.colour_theme["fg"],
                                  anchor="w",
                                  padx=10)
                
                widget.bind("<Button-1>", func=self.click_func)
                widget.bind("<Enter>", func=self.enter_func)
                widget.bind("<Leave>", func=self.leave_func)

                return widget
            
            
        class PlaylistTop(AbstractMenuItem):

            def __init__(self, 
                         MainWindow,
                         master: tk.Misc) -> None:
                
                self.arrow_text_var = tk.StringVar(value="▼")
                self.current_status = "retracted"

                super().__init__(MainWindow, master)


            def click_func(self, event) -> None:

                if self.current_status == "retracted":

                    self.arrow_text_var.set("▲")
                    self.current_status = "expanded"
                    self.MainWindow.menu_playlists.expand()

                elif self.current_status == "expanded":

                    self.arrow_text_var.set("▼")
                    self.current_status = "retracted"
                    self.MainWindow.menu_playlists.retract()
            

            def enter_func(self, event) -> None:
                self.widget.config(bg=self.colour_theme["hover_bg"])

                children: list[Any] = self.widget.winfo_children()
                for child in children:
                    child.config(bg=self.colour_theme["hover_bg"])


            def leave_func(self, event) -> None:
                self.widget.config(bg=self.colour_theme["menu_bg"])

                children: list[Any] = self.widget.winfo_children()
                for child in children:
                    child.config(bg=self.colour_theme["menu_bg"])
            

            def as_tk_widget(self) -> tk.Frame:
                try:
                    return self.widget
                except AttributeError:
                    pass

                self.widget = tk.Frame(self.master, 
                                       bg=self.colour_theme["menu_bg"])
                
                playlist_text = tk.Label(self.widget, text="Playlist", 
                                         bg=self.colour_theme["menu_bg"],
                                         fg=self.colour_theme["fg"],
                                         anchor="w",
                                         padx=10)
                
                arrow = tk.Label(self.widget, 
                                 textvariable=self.arrow_text_var,
                                 bg=self.colour_theme["menu_bg"],
                                 fg=self.colour_theme["fg"],
                                 anchor="e",
                                 padx=10)
                

                self.widget.bind("<Button-1>", func=self.click_func)
                playlist_text.bind("<Button-1>", func=self.click_func)
                arrow.bind("<Button-1>", func=self.click_func)

                self.widget.bind("<Enter>", func=self.enter_func)
                self.widget.bind("<Leave>", func=self.leave_func)
                
                playlist_text.pack(side="left")
                arrow.pack(side="right")

                return self.widget
            

        class Playlists(AbstractMenuItem):

            def __init__(self, 
                         MainWindow,
                         master: tk.Frame) -> None:
                
                super().__init__(MainWindow, master)

                self.window = MainWindow._MainPanel.PlaylistWin

                self.all_playlists = (
                    Backend._PlaylistsControl.playlists_names)
                self.playlist_display = []

                self.playlists_frame = tk.Frame(
                    self.widget,
                    bg=self.colour_theme["menu_bg"])
                self.playlists_frame.grid_columnconfigure(0, weight=1)
                
                self.display_frame_colour_theme = {
                    "bg": self.colour_theme["menu_bg"],
                    "hover_bg": self.colour_theme["hover_bg"],
                    "fg": self.colour_theme["fg"]
                }


            def click_func(self, display_id: int) -> None:
                self.MainWindow._MainPanel.set_active_frame(self.window)
                self.window.playlist_index = display_id


            def as_tk_widget(self) -> tk.Frame:
                frame = tk.Frame(self.master, 
                                 bg=self.colour_theme["menu_bg"])
                frame.columnconfigure(0, weight=1)
                
                return frame
            

            def expand(self) -> None:
                self.playlists_frame.grid(column=0, row=0,
                                          sticky="nesw")
            

            def retract(self) -> None:
                self.playlists_frame.grid_forget()
            

            def update(self) -> None:
                if len(self.playlist_display) > len(self.all_playlists):

                    delete_displays = (
                        self.playlist_display[
                            len(self.all_playlists):])
                    
                    for display_frame in delete_displays:
                        display_frame.frame.destroy()

                    del delete_displays


                    self.playlist_display = (
                        self.playlist_display[:len(self.all_playlists)])
                    
                else:
                    for i in range(len(self.playlist_display), 
                                   len(self.all_playlists)):
                        
                        display = DisplayFrame(
                            master=self.playlists_frame,
                            input_data=self.all_playlists,
                            display_id=i,
                            colour_theme=self.display_frame_colour_theme)
                        
                        display.name_lbl.config(padx=40)
                        
                        display.frame.bind(
                            "<Button-1>", 
                            lambda _, i=i: self.click_func(i))
                        display.name_lbl.bind(
                            "<Button-1>", 
                            lambda _, i=i: self.click_func(i))
                        
                        display.load_widgets()
                        display.frame.grid_rowconfigure(0, minsize=0)

                        display.frame.grid(column=0, row=i, sticky="ew")

                        self.playlist_display.append(display)


                for display_frame in self.playlist_display:
                    display_frame.update() 


        class NewPlaylist(AbstractMenuItem):
            def __init__(self, 
                         MainWindow, 
                         master: tk.Misc) -> None:
                
                super().__init__(MainWindow, master)


            def click_func(self, event) -> None:
                playlists_names = Backend._PlaylistsControl.playlists_names
                name = "New Playlist"

                i = 2
                while name in playlists_names:
                    name = f"New Playlist {i}"
                    i += 1

                Backend._PlaylistsControl.add_new_playlist(name)

                playlist_top = self.MainWindow.menu_playlist_top
                if playlist_top.current_status == "retracted":
                    playlist_top.click_func(None)


            def as_tk_widget(self) -> tk.Label:
                widget = tk.Label(self.master,
                                  text="Create New Playlist",
                                  bg=self.colour_theme["menu_bg"],
                                  fg=self.colour_theme["fg"],
                                  anchor="w",
                                  padx=10)
                
                widget.bind("<Button-1>", func=self.click_func)
                widget.bind("<Enter>", func=self.enter_func)
                widget.bind("<Leave>", func=self.leave_func)

                return widget

                

        def load_menu(self) -> None:
            self.frame.grid(column=0, row=0, rowspan=2, sticky="nesw")
            

        def add_menu_item(self, MenuItem: AbstractMenuItem) -> None:
            widget = MenuItem.widget
            widget.grid(column=0, row=(len(self.menu_widgets)),
                        sticky="ew")
            
            self.menu_items.append(MenuItem)
            self.menu_widgets.append(widget)


        def update(self) -> None:
            for menu_item in self.menu_items:
                menu_item.update()



    class AudioPlayer:

        def __init__(self, MainWindow) -> None:

            self.colour_theme = MainWindow.colour_theme

            self.timestamp = 0
            self.duration = 0
            self.volume = 1
            self.playing = False

            self.master = MainWindow.grid_frame

            self.border_frame = tk.Frame(self.master, 
                                         bg=self.colour_theme["menu_bg"])
            self.border_frame.grid_columnconfigure(0, weight=1)

            self.frame = tk.Frame(self.border_frame, 
                                  bg=self.colour_theme["bg"])

            self.progress_slider = self.Slider(
                self.frame, track_padding=20, 
                bg=self.colour_theme["bg"],
                track_colour="black",
                handle_colour="white",
                input_callback=self.slider_set_timestamp)
            

            self.default_volume_frame = tk.Frame(
                self.frame,
                bg=self.colour_theme["bg"]
            )
            
            self.set_btn = tk.Label(
                self.default_volume_frame,
                text="Save Default Volume",
                width=20,
                bg=self.colour_theme["menu_bg"],
                fg=self.colour_theme["fg"]
            )

            self.set_btn.bind(
                "<Enter>", 
                lambda _: self.set_btn.config(
                    bg=self.colour_theme["hover_bg"]))
            
            self.set_btn.bind(
                "<Leave>", 
                lambda _: self.set_btn.config(
                    bg=self.colour_theme["menu_bg"]))
            
            self.set_btn.bind(
                "<Button-1>",
                lambda _: Backend._AudioPlayer.add_default_volume(
                    path=Backend._AudioPlayer.current_path,
                    volume=Backend._AudioPlayer.volume
                )
            )

            self.remove_btn = tk.Label(
                self.default_volume_frame,
                text="Delete Default Volume",
                width=20,
                bg=self.colour_theme["menu_bg"],
                fg=self.colour_theme["fg"]
            )

            self.remove_btn.bind(
                "<Enter>", 
                lambda _: self.remove_btn.config(
                    bg=self.colour_theme["hover_bg"]))
            
            self.remove_btn.bind(
                "<Leave>", 
                lambda _: self.remove_btn.config(
                    bg=self.colour_theme["menu_bg"]))
            
            self.remove_btn.bind(
                "<Button-1>",
                lambda _: Backend._AudioPlayer.remove_default_volume(
                    Backend._AudioPlayer.current_path
                )
            )
            

            self.last_btn_img = tk.PhotoImage(
                file=os.path.join(img_path, "last_btn.png"))

            self.last_btn = tk.Label(self.frame,
                                     image=self.last_btn_img,
                                     bg=self.colour_theme["bg"])
            
            self.last_btn.bind("<Button-1>",
                               lambda _: self.play_last())
            
            self.last_btn.bind("<Enter>", 
                               lambda _: self.last_btn.config(
                                   bg=self.colour_theme["hover_bg"])
                              )
            
            self.last_btn.bind("<Leave>", 
                               lambda _: self.last_btn.config(
                                   bg=self.colour_theme["bg"])
                              )


            self.play_btn_img = tk.PhotoImage(
                file=os.path.join(img_path, "play_btn.png"))
            self.pause_btn_img = tk.PhotoImage(
                file=os.path.join(img_path, "pause_btn.png"))
            
            self.play_btn = tk.Label(self.frame, 
                                     image=self.play_btn_img,
                                     bg=self.colour_theme["bg"])
            
            self.play_btn.bind("<Button-1>", 
                               lambda _: self.invert_play_state())
            
            self.play_btn.bind("<Enter>", 
                               lambda _: self.play_btn.config(
                                   bg=self.colour_theme["hover_bg"])
                              )
            
            self.play_btn.bind("<Leave>", 
                               lambda _: self.play_btn.config(
                                   bg=self.colour_theme["bg"])
                              )
            

            self.next_btn_img =tk.PhotoImage(
                file=os.path.join(img_path, "next_btn.png"))

            self.next_btn = tk.Label(self.frame, 
                                     image=self.next_btn_img,
                                     bg=self.colour_theme["bg"])
            
            self.next_btn.bind("<Button-1>", 
                               lambda _: self.play_next())
            
            self.next_btn.bind("<Enter>", 
                               lambda _: self.next_btn.config(
                                   bg=self.colour_theme["hover_bg"])
                              )
            
            self.next_btn.bind("<Leave>", 
                               lambda _: self.next_btn.config(
                                   bg=self.colour_theme["bg"])
                              )
            

            self.volume_lbl = tk.Label(self.frame, text="100%",
                                       width=5,
                                       bg=self.colour_theme["bg"],
                                       fg=self.colour_theme["fg"])

            self.volume_slider = self.Slider(
                self.frame, track_padding=10,
                bg=self.colour_theme["bg"],
                track_colour="black",
                handle_colour="white",
                input_callback=self.slider_set_volume)
            
            self.volume_slider.set_arrow_interval(0.005)

            self.filename_lbl = tk.Label(self.frame, 
                                         width=30,
                                         anchor="w",
                                         bg=self.colour_theme["bg"],
                                         fg=self.colour_theme["fg"],
                                         padx=10)


        class Slider:

            def __init__(self, 
                         master: tk.Misc,
                         *,
                         track_padding: int,
                         circle_radius: int=5,
                         width: int=150,
                         bg: str,
                         track_colour: str,
                         handle_colour: str,
                         input_callback: Callable[[float], None]
                         =lambda value: None) -> None:
                
                self.master = master
                self.padding = track_padding
                self.radius = circle_radius
                self.input_callback = input_callback
                self.arrow_interval = 0

                self.width = width
                self.value = 0
                self.focused = False

                self.canvas = tk.Canvas(self.master,
                                        width=self.width, 
                                        height=20, 
                                        bg=bg,
                                        highlightthickness=0,
                                        takefocus=True)
                
                
                self.track = self.canvas.create_rectangle(
                    0, 0, 1, 1, fill=track_colour, outline="")
                
                self.handle = self.canvas.create_oval(
                    0, 0, 1, 1, fill=handle_colour, outline="")

                
                self.canvas.bind("<Configure>", self.resize)
                self.canvas.bind("<B1-Motion>", self.set_value_by_tk)
                self.canvas.bind("<Button-1>", self.set_value_by_tk)
                self.canvas.bind("<ButtonRelease-1>", self.unfocus)  

                self.canvas.bind("<Left>", self.left_arrow)
                self.canvas.bind("<Right>", self.right_arrow)
                
                

            def resize(self, event) -> None:
                self.width = event.width
                track_size = self.width - self.padding * 2
                center = int(self.value * track_size + self.padding)

                self.canvas.coords(self.track,
                                   self.padding, 
                                   9,
                                   self.width - self.padding, 
                                   11)
                
                self.canvas.coords(self.handle,
                                   center - self.radius,
                                   10 - self.radius,
                                   center + self.radius,
                                   10 + self.radius)
                

            def set_value_by_tk(self, event) -> None:
                self.focused = True
                event.widget.focus_set()

                x = event.x
                x = min(max(x, self.padding), 
                        self.width - self.padding)

                track_size = self.width - self.padding * 2
                self.value = (x - self.padding) / track_size

                self.canvas.coords(self.handle,
                                   x - self.radius,
                                   10 - self.radius,
                                   x + self.radius,
                                   10 + self.radius)
                
                self.input_callback(self.value)


            def left_arrow(self, event) -> None:
                self.value -= self.arrow_interval
                self.value = max(self.value, 0)

                self.set_value(self.value)

                self.input_callback(self.value)


            def right_arrow(self, event) -> None:
                self.value += self.arrow_interval
                self.value = min(self.value, 1)

                self.set_value(self.value)

                self.input_callback(self.value)


            def unfocus(self, event) -> None:
                self.focused = False
                

            def set_value(self, value: float) -> None:  
                if self.focused:
                    return
                        
                self.value = min(max(value, 0), 1)

                track_size = self.width - self.padding * 2
                x = int(self.value * track_size + self.padding)
                
                
                self.canvas.coords(self.handle,
                                   x - self.radius,
                                   10 - self.radius,
                                   x + self.radius,
                                   10 + self.radius)
                

            def get_value(self) -> float:
                return self.value
            
            def set_arrow_interval(self, interval: float) -> None:
                self.arrow_interval = interval
                

        def load_audio_player(self) -> None:
            self.border_frame.grid(column=1, row=1, sticky="nesw")
            self.frame.grid(column=0, row=0, sticky="nesw", 
                            pady=1)

            # for centering some widgets
            self.frame.grid_columnconfigure(1, weight=1)
            self.frame.grid_columnconfigure(5, weight=1)

            self.progress_slider.canvas.grid(column=0, row=0,
                                             sticky="nesw",
                                             columnspan=8)
            

            self.default_volume_frame.grid(column=0, row=1,
                                           sticky="nesw",
                                           columnspan=8)
            self.default_volume_frame.grid_columnconfigure(0, weight=1)
            
            self.set_btn.grid(column=1, row=0,
                              sticky="nesw")
            
            self.remove_btn.grid(column=2, row=0,
                                 sticky="nesw",
                                 padx=2)
            

            self.filename_lbl.grid(column=0, row=2, sticky="w")
            self.last_btn.grid(column=2, row=2)
            self.play_btn.grid(column=3, row=2)
            self.next_btn.grid(column=4, row=2)
            self.volume_lbl.grid(column=6, row=2)
            self.volume_slider.canvas.grid(column=7, row=2,
                                           sticky="nesw")
            
            self.volume_slider.value = self.volume / 2
            

        def load_data(self) -> None:
            self.timestamp = Backend._AudioPlayer.get_timestamp()
            self.duration = Backend._AudioPlayer.get_duration()
            self.playing = Backend._AudioPlayer.playing
            self.volume = Backend._AudioPlayer.volume

            if self.duration != 0:
                self.progress_slider.set_arrow_interval(1 / self.duration)


        def invert_play_state(self) -> None:
            Backend._AudioPlayer.invert_play_state()            
        

        def play_from_start(self) -> None:
            Backend._AudioPlayer.play_from_start()


        def play_next(self) -> None:
            Backend._PlayQueue.play_next()

        
        def play_last(self) -> None:
            Backend._PlayQueue.play_last()
            

        def goto_time(self, frame_time: float) -> None:
            Backend._AudioPlayer.goto_time(frame_time)


        def slider_set_timestamp(self, value: float) -> None:
            frame_time = value * self.duration
            self.goto_time(frame_time)


        def slider_set_volume(self, value: float) -> None:
            self.volume = value * 2
            Backend._AudioPlayer.set_volume(self.volume)


        def update(self) -> None:
            self.load_data()

            if self.duration == 0:
                progress = 0
            else:
                progress = self.timestamp / self.duration

            self.progress_slider.set_value(progress)


            self.volume_slider.set_value(self.volume / 2)
            self.volume_lbl.config(text=f"{round(self.volume * 100)}%")


            filename = os.path.basename(Backend._AudioPlayer.current_path)
            self.filename_lbl.config(text=filename)


            if self.playing:
                self.play_btn.config(image=self.pause_btn_img)
            else:
                self.play_btn.config(image=self.play_btn_img)
                
        

    class MainPanel:
        def __init__(self, MainWindow) -> None:
            
            self.colour_theme = MainWindow.colour_theme

            self.master = MainWindow.grid_frame

            self.BlankWin = self.BlankWindow(MainWindow)
            self.PlayQueueWin = self.PlayQueueWindow(MainWindow)
            self.LibraryWin = self.LibraryWindow(MainWindow)
            self.SettingsWin = self.SettingsWindow(MainWindow)
            self.PlaylistWin = self.PlaylistWindow(MainWindow)
            
            self.active_win = self.BlankWin


        class MainPanelWindow:
            
            def __init__(self, MainWindow) -> None:

                self.MainWindow = MainWindow
                self.colour_theme = MainWindow.colour_theme

                self.master = MainWindow.grid_frame

                self.frame = tk.Frame(self.master)


            def update(self) -> None:
                pass


        class BlankWindow(MainPanelWindow):

            def __init__(self, MainWindow) -> None:

                super().__init__(MainWindow)

                self.frame.config(bg=self.colour_theme["bg"])

        
        class PlayQueueWindow(MainPanelWindow):
            
            def __init__(self, MainWindow) -> None:

                super().__init__(MainWindow)

                self.play_queue = Backend._PlayQueue.play_queue
                self.checkbox_index = []

                self.play_queue_displays = []

                self.frame.config(bg=self.colour_theme["bg"])


                self.title_lbl = tk.Label(self.frame, 
                                          text="Play Queue",
                                          anchor="w",
                                          padx=50,
                                          bg=self.colour_theme["bg"],
                                          fg=self.colour_theme["fg"],
                                          font=("SystemDefaultFont", 20))
                

                self.button_frame = tk.Frame(self.frame,
                                             bg=self.colour_theme["bg"])
                
                self.button_frame.grid_columnconfigure(0, weight=1)
                self.button_frame.grid_columnconfigure(3, weight=1)


                self.play_btn = tk.Label(self.button_frame,
                                         text="Play",
                                         width=20,
                                         bg=self.colour_theme["menu_bg"],
                                         fg=self.colour_theme["fg"])
                
                self.play_btn.bind(
                    "<Button-1>", 
                    lambda _: self.play_selected())

                self.play_btn.bind("<Enter>", 
                                   self.play_btn_enter)
            
                self.play_btn.bind("<Leave>", 
                                   self.play_btn_leave)
                

                self.delete_btn = tk.Label(self.button_frame,
                                           text="Remove",
                                           width=20,
                                           bg=self.colour_theme["menu_bg"],
                                           fg=self.colour_theme["fg"])

                self.delete_btn.bind("<Button-1>", 
                                     lambda _: self.remove_by_index()
                                    )
                
                self.delete_btn.bind("<Enter>",
                                     lambda _: self.delete_btn.config(
                                         bg=self.colour_theme["hover_bg"])
                                    )
                
                self.delete_btn.bind("<Leave>",
                                     lambda _: self.delete_btn.config(
                                         bg=self.colour_theme["menu_bg"])
                                    )
                

                self.play_queue_border = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["menu_bg"],
                    padx=2,
                    pady=2)
                
                self.play_queue_frame = tk.Frame(
                    self.play_queue_border,
                    bg=self.colour_theme["bg"])
                

                self.scroll_canvas = tk.Canvas(
                    self.play_queue_frame,
                    bg=self.colour_theme["bg"],
                    highlightthickness=0)


                self.scroll_frame = tk.Frame(
                    self.scroll_canvas,
                    bg=self.colour_theme["bg"])
                

                self.scrollbar_frame = tk.Frame(
                    self.play_queue_frame,
                    bg=self.colour_theme["scrollbar_bg"],
                    width=5)
                

                self.scrollbar = tk.Frame(
                    self.scrollbar_frame,
                    bg=self.colour_theme["scrollbar_fg"])
                
                self.scrollbar.propagate(False)


                self.scroll_canvas.create_window(
                    0, 0,
                    window=self.scroll_frame,
                    anchor="nw")
                
                self.scroll_canvas.bind(
                    "<Configure>", 
                    self.resize_scroll_canvas)
                
                self.scroll_canvas.bind("<MouseWheel>", 
                                        self.mousewheel_scroll)
                

                self.load_widgets()
                        

            class PlayQueueDisplayFrame(DisplayFrame):

                def __init__(self,
                             master: tk.Frame | tk.Canvas,
                             PlayQueueWin,
                             display_id: int) -> None:

                    super().__init__(master, 
                                     PlayQueueWin.play_queue,
                                     display_id,
                                     PlayQueueWin.colour_theme)
                    
                    self.PlayQueueWin = PlayQueueWin
                    self.checkbox_index = PlayQueueWin.checkbox_index

                    self.y_offset = 0

                    self.checkbox = tk.Frame(
                        self.frame,
                        bg=self.colour_theme["menu_bg"],
                        width=10,
                        height=10)
                    
                    self.frame.bind(
                        "<MouseWheel>", 
                        self.PlayQueueWin.mousewheel_scroll)
                    
                    self.checkbox.bind(
                        "<MouseWheel>", 
                        self.PlayQueueWin.mousewheel_scroll)
                    
                    self.name_lbl.bind(
                        "<MouseWheel>", 
                        self.PlayQueueWin.mousewheel_scroll)
                    

                    self.frame.bind("<Button-1>", self.select)
                    self.checkbox.bind("<Button-1>", self.select)
                    self.name_lbl.bind("<Button-1>", self.select)

                    self.frame.bind("<B1-Motion>", self.mouse_drag)
                    self.name_lbl.bind("<B1-Motion>", self.mouse_drag)
                    # not binding on checkbox because it is short

                    self.load_widgets()


                def load_widgets(self) -> None:
                    super().load_widgets()

                    self.checkbox.grid(column=0, row=0,
                                       padx=10, pady=10)
                    
                def enter_func(self, event) -> None:
                    super().enter_func(event)

                    if self.id not in self.checkbox_index:
                        self.checkbox.config(bg=self.colour_theme["hover_bg"])


                def leave_func(self, event) -> None:
                    super().leave_func(event)

                    if self.id not in self.checkbox_index:
                        self.checkbox.config(bg=self.colour_theme["bg"])

                
                def mouse_drag(self, event) -> None:
                    height = self.frame.winfo_height()

                    y = event.y + self.y_offset * height
                    index = self.id - self.y_offset


                    if y < height * - 0.5:
                        if 0 < index <= len(self.input_data) - 1:
                            Backend._PlayQueue.swap_order(
                                index, index - 1)
                            
                            if index in self.checkbox_index:
                                self.checkbox_index[
                                    self.checkbox_index.index(index)] -= 1
                            
                            self.y_offset += 1
                            
                    elif y > height * 1.5:
                        if 0 <= index < len(self.input_data) - 1:
                            Backend._PlayQueue.swap_order(
                                index, index + 1)
                            
                            if index in self.checkbox_index:
                                self.checkbox_index[
                                    self.checkbox_index.index(index)] += 1
                            
                            self.y_offset -= 1


                def select(self, event) -> None:
                    self.y_offset = 0 # for mouse_drag

                    if self.id in self.checkbox_index:
                        self.checkbox_index.remove(self.id)
                    else:
                        self.checkbox_index.append(self.id)


                def update(self) -> None:
                    if self.id < len(self.input_data):
                        filename = os.path.basename(
                            self.input_data[self.id])
                        
                        self.name_lbl.config(text=filename)

                    else:
                        self.name_lbl.config(text="")
                        self.leave_func(None)
                        self.checkbox.config(bg=self.frame["bg"])
                        return
                    
                    
                    if self.id in self.checkbox_index:
                        self.checkbox.config(
                            bg=self.colour_theme["fg"])
                    else:
                        self.checkbox.config(
                            bg=self.colour_theme["menu_bg"])



            def load_widgets(self) -> None:
                self.frame.grid_columnconfigure(0, weight=1)
                self.frame.grid_rowconfigure(2, weight=1)

                self.title_lbl.grid(column=0, row=0, sticky="nesw",
                                    pady=10)


                self.button_frame.grid(column=0, row=1)

                self.play_btn.grid(column=1, row=0, padx=1)
                self.delete_btn.grid(column=2, row=0, padx=1)


                self.play_queue_border.grid(column=0, row=2, sticky="nesw",
                                            padx=50, pady=10)
                self.play_queue_border.grid_columnconfigure(0, weight=1)
                self.play_queue_border.grid_rowconfigure(0, weight=1)

                self.play_queue_frame.grid(column=0, row=0, sticky="nesw")
                self.play_queue_frame.grid_columnconfigure(0, weight=1)
                self.play_queue_frame.grid_rowconfigure(0, weight=1)

                self.scroll_canvas.grid(column=0, row=0, sticky="nesw")

                self.scrollbar_frame.grid(column=1, row=0, sticky="ns")
                self.scrollbar.place(x=0, rely=0, relwidth=1, relheight=1)


            def play_selected(self) -> None:
                if len(self.checkbox_index) == 1:
                    index = self.checkbox_index[0]
                    Backend._PlayQueue.play_index(index)
                elif len(self.checkbox_index) == 0:
                    Backend._PlayQueue.play_index(0)


            def remove_by_index(self) -> None:
                Backend._PlayQueue.remove_by_index(
                    self.checkbox_index)
                
                self.checkbox_index.clear()


            def adjust_scrollbar(self) -> None:
                self.scroll_canvas.config(
                    scrollregion=self.scroll_canvas.bbox("all"))
                
                top, bot = self.scroll_canvas.yview()
                self.scrollbar.place_configure(
                    rely=top, 
                    relheight=(bot - top))


            def resize_scroll_canvas(self, event) -> None:
                self.scroll_frame.grid_columnconfigure(
                    0, minsize=event.width)

                self.adjust_scrollbar()
                

            def mousewheel_scroll(self, event) -> None:
                if event.delta > 0:
                    if self.scroll_canvas.yview()[0] != 0:
                        self.scroll_canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    if self.scroll_canvas.yview()[1] != 1:
                        self.scroll_canvas.yview_scroll(1, "units")
                else:
                    return
                    

            def play_btn_enter(self, event) -> None:
                if len(self.checkbox_index) <= 1:
                    self.play_btn.config(
                        bg=self.colour_theme["hover_bg"])


            def play_btn_leave(self, event) -> None:
                if len(self.checkbox_index) <= 1:
                    self.play_btn.config(
                        bg=self.colour_theme["menu_bg"])


            def update(self) -> None:
                if len(self.play_queue_displays) > len(self.play_queue):

                    delete_displays = (
                        self.play_queue_displays[
                            len(self.play_queue):])
                    
                    for display_frame in delete_displays:
                        display_frame.frame.destroy()

                    del delete_displays


                    self.play_queue_displays = (
                        self.play_queue_displays[:len(self.play_queue)])
                    
                else:
                    for i in range(len(self.play_queue_displays), 
                                   len(self.play_queue)):
                        
                        display = self.PlayQueueDisplayFrame(
                            master=self.scroll_frame,
                            PlayQueueWin=self,
                            display_id=i)
                        
                        
                        display.frame.grid(column=0, row=i, sticky="ew")

                        self.play_queue_displays.append(display)


                for display_frame in self.play_queue_displays:
                    display_frame.update()


                if len(self.checkbox_index) > 1:
                    self.play_btn.config(bg=self.colour_theme["disabled_bg"])

                elif self.play_btn["bg"] == self.colour_theme["disabled_bg"]:
                    self.play_btn_leave(None)


                self.adjust_scrollbar()



        class LibraryWindow(MainPanelWindow):
            
            def __init__(self, MainWindow) -> None:

                super().__init__(MainWindow)

                self.file_paths = Backend._Library.file_paths
                self.checkbox_index = []

                self.file_displays = []

                self.target_options = ["Cancel", "Play Queue"]
                self.target_displays = []


                self.frame.config(bg=self.colour_theme["bg"])

                self.title_frame = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["bg"])


                self.title_lbl = tk.Label(
                    self.title_frame, 
                    text="Music Library",
                    anchor="w",
                    padx=50,
                    bg=self.colour_theme["bg"],
                    fg=self.colour_theme["fg"],
                    font=("SystemDefaultFont", 20))
                

                self.settings_btn = tk.Label(
                    self.title_frame,
                    text="Settings",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"])
                
                self.settings_btn.bind(
                    "<Button-1>", self.open_settings)

                self.settings_btn.bind(
                    "<Enter>",
                    lambda _: self.settings_btn.config(
                        bg=self.colour_theme["hover_bg"]))
                
                self.settings_btn.bind(
                    "<Leave>",
                    lambda _: self.settings_btn.config(
                        bg=self.colour_theme["menu_bg"]))
                          

                self.button_frame = tk.Frame(self.frame,
                                             bg=self.colour_theme["bg"])


                self.add_btn = tk.Label(
                    self.button_frame,
                    text="Add to ...",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"])
                
                self.add_btn.bind("<Button-1>", self.add_to)
                
                self.add_btn.bind("<Enter>",
                                  self.add_btn_enter)
                
                self.add_btn.bind("<Leave>",
                                  self.add_btn_leave)
                

                self.refresh_btn = tk.Label(
                    self.button_frame,
                    text="Refresh",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"])
                
                self.refresh_btn.bind("<Button-1>", self.refresh)

                self.refresh_btn.bind(
                    "<Enter>",
                    lambda _: self.refresh_btn.config(
                        bg=self.colour_theme["hover_bg"]))
                
                self.refresh_btn.bind(
                    "<Leave>",
                    lambda _: self.refresh_btn.config(
                        bg=self.colour_theme["menu_bg"]))

                
                self.target_border = tk.Frame(
                    self.button_frame,
                    bg=self.colour_theme["menu_bg"],
                    padx=2,
                    pady=2)
                
                self.target_frame = tk.Frame(
                    self.target_border,
                    bg=self.colour_theme["fg"])

                self.target_scroll_canvas = tk.Canvas(
                    self.target_frame,
                    bg=self.colour_theme["bg"],
                    highlightthickness=0)
                
                self.target_scroll_frame = tk.Frame(
                    self.target_scroll_canvas,
                    bg=self.colour_theme["bg"])
                
                self.target_scrollbar_frame = tk.Frame(
                    self.target_frame,
                    bg=self.colour_theme["scrollbar_bg"],
                    width=5)
                
                self.target_scrollbar = tk.Frame(
                    self.target_scrollbar_frame,
                    bg=self.colour_theme["scrollbar_fg"])
                
                self.target_scrollbar.propagate(False)

                self.target_scroll_canvas.create_window(
                    0, 0,
                    window=self.target_scroll_frame,
                    anchor="nw")
                
                self.target_scroll_canvas.bind(
                    "<Configure>",
                    self.resize_target_scroll_canvas)
                
                self.target_scroll_canvas.bind(
                    "<MouseWheel>", 
                    self.target_mousewheel_scroll)
                

                self.library_border = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["menu_bg"],
                    padx=2,
                    pady=2)
                
                self.library_frame = tk.Frame(
                    self.library_border,
                    bg=self.colour_theme["bg"])
                

                self.scroll_canvas = tk.Canvas(
                    self.library_frame,
                    bg=self.colour_theme["bg"],
                    highlightthickness=0)


                self.scroll_frame = tk.Frame(
                    self.scroll_canvas,
                    bg=self.colour_theme["bg"])
                

                self.scrollbar_frame = tk.Frame(
                    self.library_frame,
                    bg=self.colour_theme["scrollbar_bg"],
                    width=5)
                

                self.scrollbar = tk.Frame(
                    self.scrollbar_frame,
                    bg=self.colour_theme["scrollbar_fg"])
                
                self.scrollbar.propagate(False)

                self.scroll_canvas.create_window(
                    0, 0,
                    window=self.scroll_frame,
                    anchor="nw")
                
                self.scroll_canvas.bind(
                    "<Configure>", 
                    self.resize_scroll_canvas)
                
                self.scroll_canvas.bind(
                    "<MouseWheel>", 
                    self.library_mousewheel_scroll)
                

                self.load_widgets()
                        

            class LibraryDisplayFrame(DisplayFrame):

                def __init__(self, 
                             master: tk.Frame | tk.Canvas,
                             LibraryWin,
                             display_id: int) -> None:
                    
                    super().__init__(master, 
                                     LibraryWin.file_paths, 
                                     display_id, 
                                     LibraryWin.colour_theme)
                    
                    self.LibraryWin = LibraryWin

                    self.checkbox_index = LibraryWin.checkbox_index

                    self.checkbox = tk.Frame(
                        self.frame,
                        bg=self.colour_theme["menu_bg"],
                        width=10,
                        height=10)
                    
                    self.frame.bind(
                        "<MouseWheel>", 
                        self.LibraryWin.library_mousewheel_scroll)
                    
                    self.checkbox.bind(
                        "<MouseWheel>", 
                        self.LibraryWin.library_mousewheel_scroll)
                    
                    self.name_lbl.bind(
                        "<MouseWheel>", 
                        self.LibraryWin.library_mousewheel_scroll)
                    

                    self.frame.bind("<Button-1>", self.select)
                    self.checkbox.bind("<Button-1>", self.select)
                    self.name_lbl.bind("<Button-1>", self.select)


                    self.load_widgets()


                def load_widgets(self) -> None:
                    super().load_widgets()

                    self.checkbox.grid(column=0, row=0,
                                       padx=10, pady=10)
                    

                def enter_func(self, event) -> None:
                    super().enter_func(event)

                    if self.id not in self.checkbox_index:
                        self.checkbox.config(bg=self.colour_theme["hover_bg"])


                def leave_func(self, event) -> None:
                    super().leave_func(event)

                    if self.id not in self.checkbox_index:
                        self.checkbox.config(bg=self.colour_theme["bg"])

                
                def select(self, event) -> None:
                    if self.id in self.checkbox_index:
                        self.checkbox_index.remove(self.id)
                    else:
                        self.checkbox_index.append(self.id)


                def update(self) -> None:
                    if self.id < len(self.input_data):
                        self.name_lbl.config(
                            text=self.input_data[self.id])

                    else:
                        self.name_lbl.config(text="")
                        self.leave_func(None)
                        self.checkbox.config(bg=self.frame["bg"])
                        return
                    
                    if self.id in self.checkbox_index:
                        self.checkbox.config(
                            bg=self.colour_theme["fg"])
                    else:
                        self.checkbox.config(
                            bg=self.colour_theme["menu_bg"])
                        

            class TargetDisplayFrame(DisplayFrame):

                def __init__(self,
                             master: tk.Frame | tk.Canvas,
                             LibraryWin,
                             display_id: int) -> None:
                    
                    super().__init__(master,
                                     LibraryWin.target_options,
                                     display_id,
                                     LibraryWin.colour_theme)
                    
                    self.LibraryWin = LibraryWin

                    self.frame.bind(
                        "<MouseWheel>",
                        self.LibraryWin.target_mousewheel_scroll)
                
                    self.name_lbl.bind(
                        "<MouseWheel>",
                        self.LibraryWin.target_mousewheel_scroll)
                    
                    self.frame.bind(
                        "<Button-1>", 
                        lambda _: LibraryWin.select_target(self.id))
                    self.name_lbl.bind(
                        "<Button-1>", 
                        lambda _: LibraryWin.select_target(self.id))
                    

                    self.name_lbl.config(padx=10)
                    self.load_widgets()
                    self.frame.grid_rowconfigure(0, minsize=20)

                    if self.id == 0:
                        self.name_lbl.config(fg=self.colour_theme["red"])


            def load_widgets(self) -> None:
                self.frame.grid_columnconfigure(0, weight=1)
                self.frame.grid_rowconfigure(2, weight=1)


                self.title_frame.grid(column=0, row=0,
                                      sticky="nesw")
                
                self.title_frame.grid_columnconfigure(1, weight=1)

                self.title_lbl.grid(column=0, row=0, 
                                    sticky="nesw",
                                    pady=10)
                
                self.settings_btn.grid(column=2, row=0,
                                       padx=(0, 50))

                self.button_frame.grid(column=0, row=1,
                                       sticky="nesw")
                
                self.button_frame.grid_columnconfigure(1, weight=1)

                self.add_btn.grid(column=0, row=0, 
                                  padx=(50, 0),
                                  sticky="nesw")
                
                self.refresh_btn.grid(column=2, row=0,
                                      padx=(0, 50),
                                      sticky="nesw")
                

                self.library_border.grid(column=0, row=2, 
                                         sticky="nesw",
                                         padx=50, pady=10)
                self.library_border.grid_columnconfigure(0, weight=1)
                self.library_border.grid_rowconfigure(0, weight=1)

                self.library_frame.grid(column=0, row=0, 
                                        sticky="nesw")
                self.library_frame.grid_columnconfigure(0, weight=1)
                self.library_frame.grid_rowconfigure(0, weight=1)

                self.scroll_canvas.grid(column=0, row=0,
                                        sticky="nesw")
                
                self.scrollbar_frame.grid(column=1, row=0, 
                                          sticky="ns")
                self.scrollbar.place(x=0, rely=0, 
                                     relwidth=1, relheight=1)
                

                self.target_border.grid_columnconfigure(0, weight=1)
                self.target_border.grid_rowconfigure(0, weight=1)

                self.target_frame.grid(column=0, row=0,
                                       sticky="nesw")
                self.target_frame.grid_columnconfigure(0, weight=1)
                self.target_frame.grid_rowconfigure(0, weight=1)

                self.target_scroll_canvas.grid(column=0, row=0)
                
                self.target_scrollbar_frame.grid(column=1, row=0,
                                                 sticky="ns")
                
                self.target_scrollbar.place(x=0, rely=0,
                                            relwidth=1, relheight=1)



            def add_to(self, event) -> None:
                if len(self.checkbox_index) != 0:
                    self.target_border.grid(column=0, row=1,
                                            columnspan=3,
                                            sticky="nw",
                                            padx=50)
                
            
            def select_target(self, display_id) -> None:
                self.target_border.grid_forget()

                if display_id == 0:
                    pass
                elif display_id == 1:
                    for index in self.checkbox_index:
                        file_path = self.file_paths[index]
                        Backend._PlayQueue.add_new_audio(file_path)

                    self.checkbox_index.clear()
                elif 2 <= display_id < len(self.target_options):
                    name = self.target_options[display_id]
                    for index in self.checkbox_index:
                        Backend._PlaylistsControl.add_new_paths(
                            name=name,
                            paths=[self.file_paths[index]]
                        )

                    self.checkbox_index.clear()


            def refresh(self, event) -> None:
                Backend._Library.load_files()


            def open_settings(self, event) -> None:
                self.MainWindow._MainPanel.set_active_frame(
                    self.MainWindow._MainPanel.SettingsWin)
            

            def add_btn_enter(self, event) -> None:
                if len(self.checkbox_index) != 0:
                    self.add_btn.config(
                        bg=self.colour_theme["hover_bg"])
                

            def add_btn_leave(self, event) -> None:
                if len(self.checkbox_index) != 0:
                    self.add_btn.config(
                        bg=self.colour_theme["menu_bg"])
                

            def adjust_scrollbar(self) -> None:
                self.scroll_canvas.config(
                    scrollregion=self.scroll_canvas.bbox("all"))
                
                top, bot = self.scroll_canvas.yview()
                self.scrollbar.place_configure(
                    rely=top, 
                    relheight=(bot - top))
                
            def adjust_target_scrollbar(self) -> None:
                self.target_scroll_canvas.config(
                    scrollregion=self.target_scroll_canvas.bbox("all"))
                
                top, bot = self.target_scroll_canvas.yview()
                self.target_scrollbar.place_configure(
                    rely=top, 
                    relheight=(bot - top))


            def resize_scroll_canvas(self, event) -> None:
                self.scroll_frame.grid_columnconfigure(
                    0, minsize=event.width)

                self.adjust_scrollbar()

            def resize_target_scroll_canvas(self, event) -> None:
                self.target_scroll_canvas.config(
                    width=self.target_scroll_frame.winfo_width(),
                    height=min(
                        self.target_scroll_frame.winfo_height(),
                        80)
                )

                self.adjust_target_scrollbar()


            def mousewheel_scroll(self, 
                                  event: tk.Event,
                                  canvas: tk.Canvas) -> None:
                if event.delta > 0:
                    if canvas.yview()[0] != 0:
                        canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    if canvas.yview()[1] != 1:
                        canvas.yview_scroll(1, "units")
                else:
                    return
                
            def library_mousewheel_scroll(self, event) -> None:
                self.mousewheel_scroll(event, self.scroll_canvas)

            def target_mousewheel_scroll(self, event) -> None:
                self.mousewheel_scroll(event, self.target_scroll_canvas)


            def update_display_frames(
                    self, 
                    display_frame_list: list[DisplayFrame],
                    input_data: list[Any],
                    DisplayFrame_cls: 
                    Type[LibraryDisplayFrame | TargetDisplayFrame],
                    master: tk.Frame
                    ) -> None:
                
                if len(display_frame_list) > len(input_data):

                    delete_displays = (
                        display_frame_list[len(input_data):])
                    
                    for display_frame in delete_displays:
                        display_frame.frame.destroy()

                    del delete_displays

                        
                    display_frame_list = (
                        display_frame_list[:len(input_data)])
                    
                else:
                    for i in range(len(display_frame_list),
                                   len(input_data)):
                        
                        display = DisplayFrame_cls(
                            master=master,
                            LibraryWin=self,
                            display_id=i)
                        
                        display.frame.grid(column=0, row=i, sticky="ew")

                        display_frame_list.append(display)

                for display_frame in display_frame_list:
                    display_frame.update()
                

            def update(self) -> None:
                self.target_options[:] = (
                    ["Cancel", "Play Queue"]
                    + Backend._PlaylistsControl.playlists_names
                )
                self.update_display_frames(
                    display_frame_list=self.file_displays,
                    input_data=self.file_paths,
                    DisplayFrame_cls=self.LibraryDisplayFrame,
                    master=self.scroll_frame)
                
                self.update_display_frames(
                    display_frame_list=self.target_displays,
                    input_data=self.target_options,
                    DisplayFrame_cls=self.TargetDisplayFrame,
                    master=self.target_scroll_frame)


                if len(self.checkbox_index) == 0:
                    self.add_btn.config(bg=self.colour_theme["disabled_bg"])

                elif self.add_btn["bg"] == self.colour_theme["disabled_bg"]:
                    self.add_btn_leave(None)


                self.adjust_scrollbar()
                self.adjust_target_scrollbar()



        class SettingsWindow(MainPanelWindow):

            def __init__(self, MainWindow) -> None:
                super().__init__(MainWindow)

                self.file_dirs = Backend._Library.file_dirs

                self.dir_displays = []

                self.frame.config(bg=self.colour_theme["bg"])


                self.title_lbl = tk.Label(
                    self.frame,
                    text="Settings",
                    anchor="w",
                    padx=50,
                    bg=self.colour_theme["bg"],
                    fg=self.colour_theme["fg"],
                    font=("SystemDefaultFont", 20))
                

                self.button_frame = tk.Frame(self.frame,
                                             bg=self.colour_theme["bg"])
                
                self.button_frame.grid_columnconfigure(0, weight=1)


                self.new_dir_btn = tk.Label(
                    self.button_frame,
                    text="Add New Directory",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"])
                
                self.new_dir_btn.bind("<Button-1>", self.add_dir)

                self.new_dir_btn.bind(
                    "<Enter>",
                    lambda _: self.new_dir_btn.config(
                        bg=self.colour_theme["hover_bg"]))
                
                self.new_dir_btn.bind(
                    "<Leave>",
                    lambda _: self.new_dir_btn.config(
                        bg=self.colour_theme["menu_bg"]))
                

                self.dir_list_border = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["menu_bg"],
                    padx=2,
                    pady=2)
                
                self.dir_list_frame = tk.Frame(
                    self.dir_list_border,
                    bg=self.colour_theme["bg"])
                

                self.scroll_canvas = tk.Canvas(
                    self.dir_list_frame,
                    bg=self.colour_theme["bg"],
                    highlightthickness=0)


                self.scroll_frame = tk.Frame(
                    self.scroll_canvas,
                    bg=self.colour_theme["bg"])
                

                self.scrollbar_frame = tk.Frame(
                    self.dir_list_frame,
                    bg=self.colour_theme["scrollbar_bg"],
                    width=5)
                

                self.scrollbar = tk.Frame(
                    self.scrollbar_frame,
                    bg=self.colour_theme["scrollbar_fg"])
                
                self.scrollbar.propagate(False)


                self.scroll_canvas.create_window(
                    0, 0,
                    window=self.scroll_frame,
                    anchor="nw")
                
                self.scroll_canvas.bind(
                    "<Configure>", 
                    self.resize_scroll_canvas)
                
                self.scroll_canvas.bind("<MouseWheel>", 
                                        self.mousewheel_scroll)
                

                self.load_widgets()
                        

            class DirsDisplayFrame:

                def __init__(self,
                             master: tk.Frame | tk.Canvas,
                             SettingsWin,
                             display_id: int) -> None:
                    
                    self.SettingsWin = SettingsWin

                    self.master = master
                    self.colour_theme = SettingsWin.colour_theme

                    self.id = display_id
                    self.file_dirs = Backend._Library.file_dirs


                    self.frame = tk.Frame(
                        self.master,
                        bg=self.colour_theme["bg"])


                    self.dirname_lbl = tk.Label(
                        self.frame,
                        text="",
                        anchor="w",
                        bg=self.colour_theme["bg"],
                        fg=self.colour_theme["fg"],
                        padx=20)


                    self.delete_btn = tk.Label(
                        self.frame,
                        text="x",
                        bg=self.colour_theme["bg"],
                        fg=self.colour_theme["fg"])
                    
                    self.delete_btn.bind("<Button-1>", self.delete_dir)
                    self.delete_btn.bind("<Enter>", self.enter_func)
                    self.delete_btn.bind("<Leave>", self.leave_func)

                    self.frame.bind(
                        "<MouseWheel>",
                        self.SettingsWin.mousewheel_scroll)
                    
                    self.dirname_lbl.bind(
                        "<MouseWheel>",
                        self.SettingsWin.mousewheel_scroll)
                    
                    self.delete_btn.bind(
                        "<MouseWheel>",
                        self.SettingsWin.mousewheel_scroll)

                    self.load_widgets()


                def load_widgets(self) -> None:
                    self.frame.grid_columnconfigure(0, weight=1)
                    self.frame.grid_columnconfigure(2, minsize=20)
                    self.frame.grid_rowconfigure(0, minsize=30)

                    self.dirname_lbl.grid(column=0, row=0,
                                          sticky="nesw")
                    
                    self.delete_btn.grid(column=1, row=0)


                def enter_func(self, event) -> None:
                    self.frame.config(
                        bg=self.colour_theme["hover_bg"])
                    self.dirname_lbl.config(
                        bg=self.colour_theme["hover_bg"])
                    self.delete_btn.config(
                        bg=self.colour_theme["hover_bg"])
                    

                def leave_func(self, event) -> None:
                    self.frame.config(
                        bg=self.colour_theme["bg"])
                    self.dirname_lbl.config(
                        bg=self.colour_theme["bg"])
                    self.delete_btn.config(
                        bg=self.colour_theme["bg"])
                    

                def delete_dir(self, event) -> None:
                    directory = self.file_dirs[self.id]
                    Backend._Library.remove_file_dir(directory)


                def update(self) -> None:
                    if self.id < len(self.file_dirs):
                        self.dirname_lbl.config(
                            text=self.file_dirs[self.id])
                    else:
                        self.dirname_lbl.config(text="")


            def load_widgets(self) -> None:
                self.frame.grid_columnconfigure(0, weight=1)
                self.frame.grid_rowconfigure(2, weight=1)

                self.title_lbl.grid(column=0, row=0,
                                    sticky="nesw",
                                    pady=10)
                
                self.button_frame.grid(column=0, row=1,
                                       sticky="nesw")
                
                self.new_dir_btn.grid(column=1, row=1,
                                      padx=(0, 50),
                                      sticky="nesw")
                
                self.dir_list_border.grid(column=0, row=2,
                                          sticky="nesw",
                                          padx=50, pady=10)
                self.dir_list_border.grid_columnconfigure(0, weight=1)
                self.dir_list_border.grid_rowconfigure(0, weight=1)

                self.dir_list_frame.grid(column=0, row=0,
                                         sticky="nesw")
                self.dir_list_frame.grid_columnconfigure(0, weight=1)
                self.dir_list_frame.grid_rowconfigure(0, weight=1)

                self.scroll_canvas.grid(column=0, row=0,
                                        sticky="nesw")
                
                self.scrollbar_frame.grid(column=1, row=0,
                                          sticky="ns")
                self.scrollbar.place(x=0, rely=0,
                                     relwidth=1, relheight=1)
                


            def add_dir(self, event) -> None:
                directory = filedialog.askdirectory()
                if directory != "":
                    Backend._Library.add_file_dir(directory)


            def adjust_scrollbar(self) -> None:
                self.scroll_canvas.config(
                    scrollregion=self.scroll_canvas.bbox("all"))
                
                top, bot = self.scroll_canvas.yview()
                self.scrollbar.place_configure(
                    rely=top, 
                    relheight=(bot - top))


            def resize_scroll_canvas(self, event) -> None:
                self.scroll_frame.grid_columnconfigure(
                    0, minsize=event.width)
                
                self.adjust_scrollbar()


            def mousewheel_scroll(self, event) -> None:
                if event.delta > 0:
                    if self.scroll_canvas.yview()[0] != 0:
                        self.scroll_canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    if self.scroll_canvas.yview()[1] != 1:
                        self.scroll_canvas.yview_scroll(1, "units")
                else:
                    return


            def update(self) -> None:
                if len(self.dir_displays) >= len(self.file_dirs):

                    delete_displays = (
                        self.dir_displays[len(self.file_dirs):])
                    
                    for display_frame in delete_displays:
                        display_frame.frame.destroy()

                    del delete_displays


                    self.dir_displays = (
                        self.dir_displays[:len(self.file_dirs)])
                    
                else:
                    for i in range(len(self.dir_displays),
                                   len(self.file_dirs)):
                        
                        display = self.DirsDisplayFrame(
                            master=self.scroll_frame,
                            SettingsWin=self,
                            display_id=i)
                        
                        display.frame.grid(column=0, row=i, sticky="ew")

                        self.dir_displays.append(display)

                for display_frame in self.dir_displays:
                    display_frame.update()


                self.adjust_scrollbar()


        class PlaylistWindow(MainPanelWindow):

            def __init__(self, MainWindow) -> None:
                super().__init__(MainWindow)

                self.playlist_index = 0
                self.current_name = ""
                self.prev_current_name = ""
                self.playlist_items = []
                
                self.item_displays = []
                self.checkbox_index = []


                self.frame.config(bg=self.colour_theme["bg"])

                self.title_frame = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["bg"]
                )
                
                self.title_lbl = tk.Label(
                    self.title_frame,
                    text="Playlist: ",
                    anchor="w",
                    bg=self.colour_theme["bg"],
                    fg=self.colour_theme["fg"],
                    font=("SystemDefaultFont", 20)
                )

                self.entry_border = tk.Frame(
                    self.title_frame,
                    bg=self.colour_theme["menu_bg"],
                    padx=2,
                    pady=2
                )

                self.playlist_name_entry = tk.Entry(
                    self.entry_border,
                    borderwidth=0,
                    width=2, 
                    bg=self.colour_theme["bg"],
                    fg=self.colour_theme["fg"],
                    insertbackground=self.colour_theme["fg"],
                    font=("SystemDefaultFont", 20)
                )

                self.playlist_name_entry.bind(
                    "<FocusOut>",
                    lambda _: self.override_entry()
                )

                self.playlist_name_entry.bind(
                    "<Double-Button-1>",
                    lambda _: self.save_entry_input()
                )

                self.playlist_name_entry.bind(
                    "<Button-3>",
                    lambda _: self.discard_entry_input()
                )


                self.button_frame = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["bg"]
                )

                self.remove_btn = tk.Label(
                    self.button_frame,
                    text="Remove",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"]
                )

                self.remove_btn.bind(
                    "<Button-1>", 
                    lambda _: self.remove_items()
                )
                
                self.remove_btn.bind(
                    "<Enter>", 
                    self.remove_btn_enter
                )

                self.remove_btn.bind(
                    "<Leave>",
                    self.remove_btn_leave
                )


                self.add_playlist_btn = tk.Label(
                    self.button_frame,
                    text="Add To Play Queue",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"]
                )

                self.add_playlist_btn.bind(
                    "<Button-1>",
                    lambda _: self.add_playlist()
                )

                self.add_playlist_btn.bind(
                    "<Enter>",
                    lambda _: self.add_playlist_btn.config(
                        bg=self.colour_theme["hover_bg"])
                )
                
                self.add_playlist_btn.bind(
                    "<Leave>",
                    lambda _: self.add_playlist_btn.config(
                        bg=self.colour_theme["menu_bg"])
                )


                self.delete_btn = tk.Label(
                    self.button_frame, 
                    text="Delete This Playlist",
                    width=20,
                    bg=self.colour_theme["menu_bg"],
                    fg=self.colour_theme["fg"]
                )

                self.delete_btn.bind(
                    "<Button-1>", 
                    lambda _: self.delete_playlist()
                )
                
                self.delete_btn.bind(
                    "<Enter>",
                    lambda _: self.delete_btn.config(
                        bg=self.colour_theme["hover_bg"])
                )
                
                self.delete_btn.bind(
                    "<Leave>",
                    lambda _: self.delete_btn.config(
                        bg=self.colour_theme["menu_bg"])
                )


                self.playlist_border = tk.Frame(
                    self.frame,
                    bg=self.colour_theme["menu_bg"],
                    padx=2,
                    pady=2
                )
                
                self.playlist_frame = tk.Frame(
                    self.playlist_border,
                    bg=self.colour_theme["bg"]
                )
                

                self.scroll_canvas = tk.Canvas(
                    self.playlist_frame,
                    bg=self.colour_theme["bg"],
                    highlightthickness=0
                )


                self.scroll_frame = tk.Frame(
                    self.scroll_canvas,
                    bg=self.colour_theme["bg"]
                )
                

                self.scrollbar_frame = tk.Frame(
                    self.playlist_frame,
                    bg=self.colour_theme["scrollbar_bg"],
                    width=5
                )
                

                self.scrollbar = tk.Frame(
                    self.scrollbar_frame,
                    bg=self.colour_theme["scrollbar_fg"]
                )
                
                self.scrollbar.propagate(False)


                self.scroll_canvas.create_window(
                    0, 0,
                    window=self.scroll_frame,
                    anchor="nw"
                )
                
                self.scroll_canvas.bind(
                    "<Configure>", 
                    self.resize_scroll_canvas
                )
                
                self.scroll_canvas.bind(
                    "<MouseWheel>", 
                    self.mousewheel_scroll
                )
                

                self.load_widgets()


            class PlaylistDisplayFrame(DisplayFrame):

                def __init__(self,
                             master: tk.Frame | tk.Canvas,
                             PlaylistWin,
                             display_id: int) -> None:

                    super().__init__(master, 
                                     PlaylistWin.playlist_items,
                                     display_id,
                                     PlaylistWin.colour_theme
                    )
                    
                    self.PlaylistWin = PlaylistWin
                    self.checkbox_index = PlaylistWin.checkbox_index

                    self.y_offset = 0

                    self.checkbox = tk.Frame(
                        self.frame,
                        bg=self.colour_theme["menu_bg"],
                        width=10,
                        height=10)
                    
                    self.frame.bind(
                        "<MouseWheel>", 
                        self.PlaylistWin.mousewheel_scroll
                    )
                    
                    self.checkbox.bind(
                        "<MouseWheel>", 
                        self.PlaylistWin.mousewheel_scroll
                    )
                    
                    self.name_lbl.bind(
                        "<MouseWheel>", 
                        self.PlaylistWin.mousewheel_scroll
                    )
                    

                    self.frame.bind("<Button-1>", self.select)
                    self.checkbox.bind("<Button-1>", self.select)
                    self.name_lbl.bind("<Button-1>", self.select)

                    self.frame.bind("<B1-Motion>", self.mouse_drag)
                    self.name_lbl.bind("<B1-Motion>", self.mouse_drag)
                    # not binding on checkbox because it is short

                    self.load_widgets()


                def load_widgets(self) -> None:
                    super().load_widgets()

                    self.checkbox.grid(column=0, row=0,
                                       padx=10, pady=10)
                    
                def enter_func(self, event) -> None:
                    super().enter_func(event)

                    if self.id not in self.checkbox_index:
                        self.checkbox.config(bg=self.colour_theme["hover_bg"])


                def leave_func(self, event) -> None:
                    super().leave_func(event)

                    if self.id not in self.checkbox_index:
                        self.checkbox.config(bg=self.colour_theme["bg"])

                
                def mouse_drag(self, event) -> None:
                    height = self.frame.winfo_height()

                    y = event.y + self.y_offset * height
                    index = self.id - self.y_offset


                    if y < height * - 0.5:
                        if 0 < index <= len(self.input_data) - 1:
                            Backend._PlaylistsControl.swap_order(
                                self.PlaylistWin.current_name,
                                index, index - 1
                            )
                            
                            if index in self.checkbox_index:
                                self.checkbox_index[
                                    self.checkbox_index.index(index)] -= 1
                            
                            self.y_offset += 1
                            
                    elif y > height * 1.5:
                        if 0 <= index < len(self.input_data) - 1:
                            Backend._PlaylistsControl.swap_order(
                                self.PlaylistWin.current_name,
                                index, index + 1
                            )
                            
                            if index in self.checkbox_index:
                                self.checkbox_index[
                                    self.checkbox_index.index(index)] += 1
                            
                            self.y_offset -= 1


                def select(self, event) -> None:
                    self.y_offset = 0 # for mouse_drag

                    if self.id in self.checkbox_index:
                        self.checkbox_index.remove(self.id)
                    else:
                        self.checkbox_index.append(self.id)


                def update(self) -> None:
                    if self.id < len(self.input_data):
                        filename = os.path.basename(
                            self.input_data[self.id])
                        
                        self.name_lbl.config(text=filename)

                    else:
                        self.name_lbl.config(text="")
                        self.leave_func(None)
                        self.checkbox.config(bg=self.frame["bg"])
                        return
                    
                    
                    if self.id in self.checkbox_index:
                        self.checkbox.config(
                            bg=self.colour_theme["fg"])
                    else:
                        self.checkbox.config(
                            bg=self.colour_theme["menu_bg"])


            def load_widgets(self) -> None:
                self.frame.grid_columnconfigure(0, weight=1)
                self.frame.grid_rowconfigure(2, weight=1)

                self.title_frame.grid(column=0, row=0, 
                                      sticky="nesw")
                
                self.title_lbl.grid(column=0, row=0,
                                    sticky="nesw",
                                    padx=(50, 0),
                                    pady=10)
                
                self.entry_border.grid(column=1, row=0,
                                       sticky="nesw",
                                       pady=10)
                
                self.playlist_name_entry.grid(column=0, row=0,
                                              sticky="nesw")
                

                self.button_frame.grid(column=0, row=1,
                                       sticky="nesw")
                self.button_frame.grid_columnconfigure(1, weight=1)
                
                self.remove_btn.grid(column=0, row=0,
                                     sticky="nesw",
                                     padx=(50, 0))
                
                self.add_playlist_btn.grid(column=2, row=0,
                                           sticky="nesw")
                
                self.delete_btn.grid(column=3, row=0,
                                     sticky="nesw",
                                     padx=(2, 50))
                
                
                self.playlist_border.grid(column=0, row=2, 
                                          sticky="nesw",
                                          padx=50, pady=10)
                self.playlist_border.grid_columnconfigure(0, weight=1)
                self.playlist_border.grid_rowconfigure(0, weight=1)

                self.playlist_frame.grid(column=0, row=0, sticky="nesw")
                self.playlist_frame.grid_columnconfigure(0, weight=1)
                self.playlist_frame.grid_rowconfigure(0, weight=1)

                self.scroll_canvas.grid(column=0, row=0, sticky="nesw")

                self.scrollbar_frame.grid(column=1, row=0, sticky="ns")
                self.scrollbar.place(x=0, rely=0, relwidth=1, relheight=1)


            def remove_items(self) -> None:
                Backend._PlaylistsControl.remove_by_index(
                    name=self.current_name,
                    index_list=self.checkbox_index
                )

                self.checkbox_index.clear()

            
            def add_playlist(self) -> None:
                if len(self.checkbox_index) == 0:
                    self.checkbox_index[:] = (
                        range(len(self.playlist_items))
                    )

                for index in self.checkbox_index:
                    file_path = self.playlist_items[index]
                    Backend._PlayQueue.add_new_audio(file_path)

                self.checkbox_index.clear()

                        
            def delete_playlist(self) -> None:
                Backend._PlaylistsControl.delete_playlist(
                    name=self.current_name
                )

                self.checkbox_index.clear()
            

            def override_entry(self) -> None:
                self.playlist_name_entry.delete(0, "end")
                self.playlist_name_entry.insert(0, self.current_name)


            def save_entry_input(self) -> None:
                new_name = self.playlist_name_entry.get()
                Backend._PlaylistsControl.rename(
                    self.current_name, new_name
                )
                self.frame.focus_set()


            def discard_entry_input(self) -> None:
                self.frame.focus_set()
                

            def adjust_entry(self, entry: tk.Entry) -> None:
                content = entry.get()
                font = tkfont.Font(entry, entry.cget("font"), size=20)
                width = font.measure(content)

                self.entry_border.columnconfigure(0, minsize=width + 20)


            def adjust_scrollbar(self) -> None:
                self.scroll_canvas.config(
                    scrollregion=self.scroll_canvas.bbox("all")
                )

                top, bot = self.scroll_canvas.yview()
                self.scrollbar.place_configure(
                    rely=top,
                    relheight=(bot - top)
                )


            def resize_scroll_canvas(self, event) -> None:
                self.scroll_frame.grid_columnconfigure(
                    0, minsize=event.width
                )

                self.adjust_scrollbar()


            def mousewheel_scroll(self, event) -> None:
                if event.delta > 0:
                    if self.scroll_canvas.yview()[0] != 0:
                        self.scroll_canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    if self.scroll_canvas.yview()[1] != 1:
                        self.scroll_canvas.yview_scroll(1, "units")
                else:
                    return
                

            def remove_btn_enter(self, event) -> None:
                if len(self.checkbox_index) >= 1:
                    self.remove_btn.config(
                        bg=self.colour_theme["hover_bg"]
                    )

            def remove_btn_leave(self, event) -> None:
                if len(self.checkbox_index) >= 1:
                    self.remove_btn.config(
                        bg=self.colour_theme["menu_bg"]
                    )


            def update(self) -> None:
                names = Backend._PlaylistsControl.playlists_names
                if 0 <= self.playlist_index < len(names):
                    self.current_name = names[self.playlist_index]
                else:
                    self.playlist_index = 0
                    self.current_name = ""

                self.playlist_items[:] = (
                    Backend._PlaylistsControl.get_file_paths(
                        self.current_name
                    )
                )


                if self.prev_current_name != self.current_name:
                    self.discard_entry_input()
                    self.override_entry()
                    self.checkbox_index.clear()

                self.prev_current_name = self.current_name


                if len(self.item_displays) > len(self.playlist_items):

                    delete_displays = (
                        self.item_displays[
                            len(self.playlist_items):])
                    
                    for display_frame in delete_displays:
                        display_frame.frame.destroy()

                    del delete_displays


                    self.item_displays = (
                        self.item_displays[:len(self.playlist_items)])
                    
                else:
                    for i in range(len(self.item_displays), 
                                   len(self.playlist_items)):
                        
                        display = self.PlaylistDisplayFrame(
                            master=self.scroll_frame,
                            PlaylistWin=self,
                            display_id=i)
                        
                        
                        display.frame.grid(column=0, row=i, sticky="ew")

                        self.item_displays.append(display)


                for display_frame in self.item_displays:
                    display_frame.update()


                if len(self.checkbox_index) < 1:
                    self.remove_btn.config(bg=self.colour_theme["disabled_bg"])

                elif self.remove_btn["bg"] == self.colour_theme["disabled_bg"]:
                    self.remove_btn_leave(None)

                self.adjust_scrollbar()
                self.adjust_entry(self.playlist_name_entry)

        

        def set_active_frame(self, window_obj: MainPanelWindow) -> None:
            new_frame = window_obj.frame

            self.active_win.frame.grid_remove()
            new_frame.grid(column=1, row=0, sticky="nesw")

            self.active_win = window_obj


        def update(self) -> None:
            self.active_win.update()
            

def main():
    window = MainWindow((1000, 500), colour_theme)
    window.init_window()

    while True:
        window.update()


if __name__ == "__main__":
    main()