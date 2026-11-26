"""
Command Pattern - V1 Basic: Remote Control
"""
from abc import ABC, abstractmethod
from typing import List


# Command Interface
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass


# Receivers
class Light:
    def __init__(self, location: str):
        self.location = location
        self.on = False
    
    def turn_on(self) -> None:
        self.on = True
        print(f"{self.location} light is ON")
    
    def turn_off(self) -> None:
        self.on = False
        print(f"{self.location} light is OFF")


class Fan:
    def __init__(self):
        self.speed = 0
    
    def high(self) -> None:
        self.speed = 3
        print("Fan is on HIGH")
    
    def off(self) -> None:
        self.speed = 0
        print("Fan is OFF")


# Concrete Commands
class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light
    
    def execute(self) -> None:
        self.light.turn_on()
    
    def undo(self) -> None:
        self.light.turn_off()


class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light
    
    def execute(self) -> None:
        self.light.turn_off()
    
    def undo(self) -> None:
        self.light.turn_on()


class NoCommand(Command):
    def execute(self) -> None:
        pass
    
    def undo(self) -> None:
        pass


# Invoker
class RemoteControl:
    def __init__(self, slots: int):
        no_cmd = NoCommand()
        self.on_commands: List[Command] = [no_cmd] * slots
        self.off_commands: List[Command] = [no_cmd] * slots
        self.undo_stack: List[Command] = []
    
    def set_command(self, slot: int, on_cmd: Command, off_cmd: Command) -> None:
        self.on_commands[slot] = on_cmd
        self.off_commands[slot] = off_cmd
    
    def press_on(self, slot: int) -> None:
        self.on_commands[slot].execute()
        self.undo_stack.append(self.on_commands[slot])
    
    def press_off(self, slot: int) -> None:
        self.off_commands[slot].execute()
        self.undo_stack.append(self.off_commands[slot])
    
    def press_undo(self) -> None:
        if self.undo_stack:
            print("--- Undo ---")
            self.undo_stack.pop().undo()


if __name__ == "__main__":
    remote = RemoteControl(3)
    
    living_room = Light("Living Room")
    kitchen = Light("Kitchen")
    
    remote.set_command(0, LightOnCommand(living_room), LightOffCommand(living_room))
    remote.set_command(1, LightOnCommand(kitchen), LightOffCommand(kitchen))
    
    print("=== Remote Control ===")
    remote.press_on(0)
    remote.press_on(1)
    
    remote.press_undo()
    remote.press_undo()
    
    remote.press_off(0)
