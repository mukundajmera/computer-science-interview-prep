"""
Bridge Pattern - Python Implementation
"""
from abc import ABC, abstractmethod


# ============ Implementation Interface ============

class Device(ABC):
    @abstractmethod
    def power_on(self) -> None: pass
    @abstractmethod
    def power_off(self) -> None: pass
    @abstractmethod
    def set_channel(self, ch: int) -> None: pass
    @abstractmethod
    def set_volume(self, vol: int) -> None: pass
    @abstractmethod
    def is_on(self) -> bool: pass


# ============ Concrete Implementations ============

class TV(Device):
    def __init__(self):
        self._on = False
        self._channel = 1
        self._volume = 30
    
    def power_on(self):
        self._on = True
        print("TV is ON")
    
    def power_off(self):
        self._on = False
        print("TV is OFF")
    
    def set_channel(self, ch: int):
        self._channel = ch
        print(f"TV Channel: {ch}")
    
    def set_volume(self, vol: int):
        self._volume = vol
        print(f"TV Volume: {vol}")
    
    def is_on(self) -> bool:
        return self._on


class Radio(Device):
    def __init__(self):
        self._on = False
        self._station = 88
        self._volume = 20
    
    def power_on(self):
        self._on = True
        print("Radio is ON")
    
    def power_off(self):
        self._on = False
        print("Radio is OFF")
    
    def set_channel(self, station: int):
        self._station = station
        print(f"Radio: {station} FM")
    
    def set_volume(self, vol: int):
        self._volume = vol
        print(f"Radio Volume: {vol}")
    
    def is_on(self) -> bool:
        return self._on


# ============ Abstraction ============

class RemoteControl(ABC):
    def __init__(self, device: Device):
        self._device = device  # Bridge!
        self._volume = 30
        self._channel = 1
    
    def toggle_power(self):
        if self._device.is_on():
            self._device.power_off()
        else:
            self._device.power_on()
    
    @abstractmethod
    def volume_up(self) -> None: pass
    
    @abstractmethod
    def volume_down(self) -> None: pass


# ============ Refined Abstractions ============

class BasicRemote(RemoteControl):
    def volume_up(self):
        self._volume += 1
        self._device.set_volume(self._volume)
    
    def volume_down(self):
        self._volume -= 1
        self._device.set_volume(self._volume)
    
    def channel_up(self):
        self._channel += 1
        self._device.set_channel(self._channel)


class AdvancedRemote(RemoteControl):
    def volume_up(self):
        self._volume += 1
        self._device.set_volume(self._volume)
    
    def volume_down(self):
        self._volume -= 1
        self._device.set_volume(self._volume)
    
    def mute(self):
        print("Muting...")
        self._device.set_volume(0)


if __name__ == "__main__":
    print("=== Basic Remote + TV ===")
    tv_remote = BasicRemote(TV())
    tv_remote.toggle_power()
    tv_remote.channel_up()
    tv_remote.volume_up()
    
    print("\n=== Advanced Remote + Radio ===")
    radio_remote = AdvancedRemote(Radio())
    radio_remote.toggle_power()
    radio_remote.volume_up()
    radio_remote.mute()
