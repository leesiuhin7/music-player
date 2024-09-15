from moviepy.editor import VideoFileClip
import numpy as np
import soundfile as sf
import sounddevice as sd
import threading
import time
import os
import json
from typing import Callable, Any
from abc import ABC, abstractmethod



self_path = os.path.dirname(os.path.abspath(__file__))

valid_ext = [
    ".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", 
    ".aiff", ".alac", ".m4a", ".opus", ".pcm",
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", 
    ".mpeg", ".mpg", ".webm", ".3gp", ".ts", ".vob", 
    ".m2ts", ".f4v", ".asf", ".swf", ".rm", ".divx",
    ".mxf", ".mka"
]



class Backend:
    def __init__(self) -> None:
        self._PlayQueue = self.PlayQueue(self)
        self._AudioPlayer = self.AudioPlayer(self)
        self._Library = self.Library(self)
        self._PlaylistsControl = self.PlaylistsControl(self)

        self._PlayQueue.load_classes(self)
        self._AudioPlayer.load_classes(self)
        self._Library.load_classes(self)
        self._PlaylistsControl.load_classes(self)


    def update(self) -> None:
        self._AudioPlayer.update()


    class BackendClasses:
        def load_classes(self, backend) -> None:
            self.backend = backend
            self._PlayQueue = backend._PlayQueue
            self._AudioPlayer = backend._AudioPlayer
            self._Library = backend._Library
            self._PlaylistsControl = backend._PlaylistsControl


    class PlayQueue(BackendClasses):
        def __init__(self, backend) -> None:
            self.play_queue: list[str] = []
            self.index = 0


        def play_index(self, index: int) -> None:
            if index >= len(self.play_queue):
                return
            
            self._AudioPlayer.load_file(self.play_queue[index])
            self._AudioPlayer.play_from_start()

            self.index = index


        def play_next(self) -> None:
            if len(self.play_queue) > 0:
                index = (self.index + 1) % len(self.play_queue)

                self.play_index(index)


        def play_last(self) -> None:
            index = self.index - 1
            if index >= 0:
                self.play_index(index)
            else:
                self._AudioPlayer.play_from_start()


        def add_new_audio(self, 
                          path: str, 
                          index: int | None=None) -> None:
            
            if index:
                self.play_queue.insert(index, path)
                if index <= self.index:
                    self.index += 1
            else:
                self.play_queue.append(path)


        def remove_by_index(self, index_list: list[int]) -> None:
            for count, index in enumerate(sorted(index_list)):
                new_index = index - count

                if 0 <= new_index < len(self.play_queue):
                    self.play_queue.pop(new_index)

                    if self.index >= new_index:
                        self.index = max(0, self.index - 1)


        def swap_order(self, index1: int, index2: int) -> None:
            self.play_queue[index1], self.play_queue[index2] = (
                self.play_queue[index2], self.play_queue[index1])



    class AudioPlayer(BackendClasses):
        def __init__(self, backend) -> None:
            self.playing = False
            self.timestamp = 0

            self.volume = 1
            self.manual_volume = 1

            self.audio_data = np.array([])
            self.fs = 44100
            self.blocksize = int(self.fs / 100)

            self.current_path = ""

            self.preload_data_key: list[str] = []
            self.preload_data: list[tuple[np.ndarray, int]] = []
            self.preload_buffer_size = 2

            self.preloader = threading.Thread(
                target=self.preload,
                daemon=True)

            self.thread = threading.Thread(
                target=self.thread_stream,
                daemon=True)
            self.terminate = False

            self.default_volume: list[float] = []
            self.volume_key_list: list[str] = []
            self.load_default_volume()


        def play(self) -> None:
            if not self.playing:
                self.playing = True


        def play_from_start(self) -> None:
            self.timestamp = 0
            self.playing = True
        
        
        def pause(self) -> None:
            if self.playing:
                self.playing = False


        def invert_play_state(self) -> None:
            self.playing = not self.playing


        def goto_time(self, timestamp: float) -> None:
            self.timestamp = int(timestamp * self.fs)


        def set_volume(self, volume: float) -> None:
            self.volume = volume
            self.manual_volume = volume
        

        def get_timestamp(self) -> float:
            return self.timestamp / self.fs
        

        def get_duration(self) -> float:
            return self.audio_data.shape[0] / self.fs
        

        def load_default_volume(self) -> None:
            path = os.path.join(self_path, "data", "default_volume.json")
            with open(path, "r") as file:
                data = json.load(file)

            self.volume_key_list, self.default_volume = data


        def save_default_volume(self) -> None:
            path = os.path.join(self_path, "data", "default_volume.json")
            with open(path, "w") as file:
                data = [self.volume_key_list, self.default_volume]
                json.dump(data, file)
                

        def add_default_volume(self, path: str, volume: float) -> None:
            if path not in self.volume_key_list:
                self.volume_key_list.append(path)
                self.default_volume.append(volume)
            else:
                index = self.volume_key_list.index(path)
                self.default_volume[index] = volume

            self.save_default_volume()


        def remove_default_volume(self, path: str) -> None:
            if path in self.volume_key_list:
                index = self.volume_key_list.index(path)
                self.volume_key_list.pop(index)
                self.default_volume.pop(index)

            self.save_default_volume()


        def do_default_volume(self, path: str) -> None:
            if path in self.volume_key_list:
                index = self.volume_key_list.index(path)
                self.volume = self.default_volume[index]
            else:
                self.volume = self.manual_volume


        def preload(self) -> None:
            while True:
                play_queue = self._PlayQueue.play_queue.copy()
                index = self._PlayQueue.index

                dist_list = [
                    self.dist_from_index(path, index, play_queue) 
                    for path in self.preload_data_key]
                
                if len(dist_list) == 0:
                    dist_list = [0]
                
                if max(dist_list) > self.preload_buffer_size:
                    index = dist_list.index(max(dist_list))
                    self.preload_data.pop(index)
                    self.preload_data_key.pop(index)
                    
                path = self.preload_choice()
                if path:
                    self.preload_file(path)
                
                time.sleep(0.1)


        def dist_from_index(self, 
                            element: Any,
                            index: int,
                            target_list: list[Any]) -> int:
            
            upper_list = target_list[index:]
            lower_list = target_list[:index + 1][::-1]

            if element in upper_list:
                upper_dist = upper_list.index(element)
            else:
                upper_dist = len(target_list)

            if element in lower_list:
                lower_dist = lower_list.index(element)
            else:
                lower_dist = len(target_list)

            return min(upper_dist, lower_dist)


        def preload_choice(self) -> str | None:
            for i in range(self.preload_buffer_size + 1):
                for sign in [1, -1]:
                    index = sign * i + self._PlayQueue.index

                    if not 0 <= index < len(self._PlayQueue.play_queue):
                        continue
                    else:
                        path = self._PlayQueue.play_queue[index]

                    if path not in self.preload_data_key:
                        return path
                    

        def preload_file(self, path: str) -> None:
            if path in self.preload_data_key:
                return
            
            try:
                audio_data, fs = sf.read(path)
            except sf.LibsndfileError:
                try:
                    audio = VideoFileClip(path).audio
                    if audio is not None:
                        audio_data = audio.to_soundarray()
                        fs = audio.fps
                    else:
                        return
                except KeyError:
                    return
                
            self.preload_data_key.append(path)
            self.preload_data.append((audio_data, fs))


        def load_file(self, path: str) -> None:
            self.stop_stream()

            if path in self.preload_data_key:
                index = self.preload_data_key.index(path)

                self.audio_data, self.fs = self.preload_data[index]
                self.blocksize = int(self.fs / 100)

                self.current_path = path

            else:
                try:
                    self.audio_data, self.fs = sf.read(path)
                    self.blocksize = int(self.fs / 100)

                    self.current_path = path

                except sf.LibsndfileError:
                    try:
                        audio = VideoFileClip(path).audio
                        if audio is not None:
                            self.audio_data = audio.to_soundarray()
                            self.fs = audio.fps
                            self.blocksize = int(self.fs / 100)

                            self.current_path = path
                            
                        else:
                            self.audio_data = np.array([])
                    except KeyError:
                        self.audio_data = np.array([])


            self.do_default_volume(path)

            self.start_stream()


        def stream_callback(self, 
                            outdata: np.ndarray, 
                            frames: int, 
                            time: Any, 
                            status: sd.CallbackFlags) -> None:
            
            end = self.timestamp + frames
            chunk = self.audio_data[self.timestamp:end]

            if len(chunk.shape) != 2:
                return

            outdata[:] = np.zeros((frames, chunk.shape[1]))

            if self.playing:
                outdata[:chunk.shape[0]] = chunk * self.volume
                self.timestamp += frames


        def thread_stream(self) -> None:
            with sd.OutputStream(
                samplerate=self.fs, 
                channels=self.audio_data.shape[1],
                callback=self.stream_callback,
                blocksize=self.blocksize) as stream:

                while not self.terminate:
                    time.sleep(0.01)

                self.terminate = False


        def start_stream(self) -> None:
            self.thread = threading.Thread(
                target=self.thread_stream,
                daemon=True)
            
            self.thread.start()


        def stop_stream(self) -> None:
            if self.thread.is_alive():
                self.terminate = True
                while self.terminate and self.thread.is_alive():
                    pass
                self.terminate = False


        def update(self) -> None:
            if not self.preloader.is_alive():
                self.preloader.start()

            if self.audio_data.shape[0] <= self.timestamp:
                if self.playing:
                    self._PlayQueue.play_next()

            if len(self._PlayQueue.play_queue) == 0:
                self.stop_stream()
                self.current_path = ""
                self.audio_data = np.array([])

                self._PlayQueue.index = -1 
                # so that it starts from the start, not the second


    
    class Library(BackendClasses):

        def __init__(self, backend) -> None:
            self.file_dirs: list[str] = []
            self.file_paths: list[str] = []

            self.load_file_dirs()
            self.load_files()


        def load_file_dirs(self) -> None:
            path = os.path.join(self_path, "data", 
                                "library_dirs.json")
            
            with open(path, "r") as file:
                data = json.load(file)

            self.file_dirs = data


        def add_file_dir(self, directory: str) -> None:
            if directory not in self.file_dirs:
                self.file_dirs.append(directory)

                path = os.path.join(self_path, "data", 
                                    "library_dirs.json")

                with open(path, "w") as file:
                    json.dump(self.file_dirs, file)

                self.load_files()


        def remove_file_dir(self, directory: str) -> None:
            if directory in self.file_dirs:
                self.file_dirs.remove(directory)

                path = os.path.join(self_path, "data", 
                                    "library_dirs.json")

                with open(path, "w") as file:
                    json.dump(self.file_dirs, file)

                self.load_files()


        def load_files(self) -> None:
            self.file_paths.clear()

            for dirs in self.file_dirs:
                with os.scandir(dirs) as entries:
                    for entry in entries:
                        root, ext = os.path.splitext(entry.name)
                        if entry.is_file() and ext.lower() in valid_ext:
                            self.file_paths.append(entry.path)

        
    class PlaylistsControl(BackendClasses):

        def __init__(self, backend) -> None:            
            self.data_path = os.path.join(self_path, "data",
                                          "playlist_data.json")
            
            self.load_playlists()


        class Playlist:
            
            def __init__(self, 
                         name: str,
                         file_paths: list[str] = []
                         ) -> None:
                
                self.name = name
                self.file_paths = file_paths


            def as_list(self) -> list[Any]:
                """Convert this Playlist object into a list"""
                data = [self.name] + self.file_paths

                return data
            

            def add_new_paths(self, paths: list[str]) -> None:
                for path in paths:
                    self.file_paths.append(path)


            def remove_by_index(self, index_list: list[int]) -> None:
                for count, index in enumerate(sorted(index_list)):
                    new_index = index - count
                    if 0 <= new_index < len(self.file_paths):
                        self.file_paths.pop(new_index)


            def swap_order(self, index1: int, index2: int) -> None:
                self.file_paths[index1], self.file_paths[index2] = (
                    self.file_paths[index2], self.file_paths[index1]
                )


            def rename(self, name: str) -> None:
                self.name = name


            def get_file_paths(self) -> list[str]:
                return self.file_paths


        def list_as_playlist(self, data: list[str]) -> Playlist:
            """Converts a list into a Playlist object"""
            return self.Playlist(name=data[0], file_paths=data[1:])

        
        def load_playlists(self) -> None:
            with open(self.data_path, "r") as file:
                data = json.load(file)

            self.playlists = []
            self.playlists_names = []

            for playlist_data in data:
                name = playlist_data[0]

                self.playlists_names.append(name)
                self.playlists.append(
                    self.list_as_playlist(playlist_data)
                )


        def save_playlists(self) -> None:
            data = []

            for playlist in self.playlists:
                data.append(playlist.as_list())

            with open(self.data_path, "w") as file:
                json.dump(data, file)


        def add_new_playlist(self, name: str) -> None:
            if name not in self.playlists_names:
                self.playlists.append(
                    self.Playlist(name=name))
                
                self.playlists_names.append(name)


        def delete_playlist(self, 
                            *, 
                            index: int = -1, 
                            name: str = ""
                            ) -> None:
            
            if index != -1:
                if 0 <= index < len(self.playlists):
                    self.playlists.pop(index)
                    self.playlists_names.pop(index)
            else:
                if name in self.playlists_names:
                    index = self.playlists_names.index(name)
                    self.playlists.pop(index)
                    self.playlists_names.pop(index)


        def playlist_from_name(self, name: str) -> Playlist | None:
            if name in self.playlists_names:
                index = self.playlists_names.index(name)
                return self.playlists[index]
            

        def add_new_paths(self, name: str, paths: list[str]) -> None:
            playlist = self.playlist_from_name(name)
            if playlist is not None:
                playlist.add_new_paths(paths)

            self.save_playlists()


        def remove_by_index(self, name: str, index_list: list[int]) -> None:
            playlist = self.playlist_from_name(name)
            if playlist is not None:
                playlist.remove_by_index(index_list)

            self.save_playlists()


        def swap_order(self, name: str, 
                       index1: int, index2: int
                       ) -> None:
            
            playlist = self.playlist_from_name(name)
            if playlist is not None:
                playlist.swap_order(index1, index2)

            self.save_playlists()


        def rename(self, name: str, new_name: str) -> None:
            playlist = self.playlist_from_name(name)
            if playlist is not None:
                index = self.playlists_names.index(name)

                playlist.rename(new_name)
                self.playlists_names[index] = new_name

            self.save_playlists()


        def get_file_paths(self, name: str) -> list[str]:
            playlist = self.playlist_from_name(name)
            if playlist is not None:
                return playlist.get_file_paths()
            else:
                return []