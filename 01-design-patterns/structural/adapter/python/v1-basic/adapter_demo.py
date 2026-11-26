"""
Adapter Pattern - V1 Basic: Media Player Adapter

Scenario: Our application expects MediaPlayer interface, but we have
third-party players with different interfaces.
"""
from abc import ABC, abstractmethod


# Target Interface - What our application expects
class MediaPlayer(ABC):
    @abstractmethod
    def play(self, filename: str) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    @abstractmethod
    def get_player_type(self) -> str:
        pass


# Adaptee 1 - Third-party VLC player with incompatible interface
class VLCPlayer:
    def play_vlc(self, file: str) -> None:
        print(f"VLC: Playing {file}")
    
    def stop_vlc(self) -> None:
        print("VLC: Stopped")


# Adaptee 2 - Another third-party player with different interface
class MP4Player:
    def load_mp4(self, filename: str) -> None:
        print(f"MP4: Loading {filename}")
    
    def start_playback(self) -> None:
        print("MP4: Playback started")
    
    def end_playback(self) -> None:
        print("MP4: Playback ended")


# Adapter for VLC Player - Uses composition (Object Adapter)
class VLCPlayerAdapter(MediaPlayer):
    def __init__(self, vlc_player: VLCPlayer = None):
        self._vlc_player = vlc_player or VLCPlayer()
    
    def play(self, filename: str) -> None:
        self._vlc_player.play_vlc(filename)
    
    def stop(self) -> None:
        self._vlc_player.stop_vlc()
    
    def get_player_type(self) -> str:
        return "VLC"


# Adapter for MP4 Player
class MP4PlayerAdapter(MediaPlayer):
    def __init__(self, mp4_player: MP4Player = None):
        self._mp4_player = mp4_player or MP4Player()
        self._current_file: str = None
    
    def play(self, filename: str) -> None:
        self._current_file = filename
        self._mp4_player.load_mp4(filename)
        self._mp4_player.start_playback()
    
    def stop(self) -> None:
        self._mp4_player.end_playback()
    
    def get_player_type(self) -> str:
        return "MP4"


# Client code - Works with any MediaPlayer
class AudioPlayerClient:
    def __init__(self):
        self._media_player: MediaPlayer = None
    
    def set_player(self, player: MediaPlayer) -> None:
        self._media_player = player
    
    def play_file(self, filename: str) -> None:
        print(f"Using {self._media_player.get_player_type()} player")
        self._media_player.play(filename)
    
    def stop_playback(self) -> None:
        self._media_player.stop()


# Demo
if __name__ == "__main__":
    client = AudioPlayerClient()
    
    # Use VLC adapter
    client.set_player(VLCPlayerAdapter())
    client.play_file("movie.vlc")
    client.stop_playback()
    
    print()
    
    # Use MP4 adapter
    client.set_player(MP4PlayerAdapter())
    client.play_file("video.mp4")
    client.stop_playback()
