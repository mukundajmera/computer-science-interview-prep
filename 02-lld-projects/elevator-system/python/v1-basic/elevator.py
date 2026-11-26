"""Elevator System Python Module."""
from enum import Enum
from typing import Dict, List
import heapq

class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"

class ElevatorState(Enum):
    MOVING = "MOVING"
    STOPPED = "STOPPED"
    MAINTENANCE = "MAINTENANCE"

class DoorState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class Request:
    def __init__(self, floor: int, direction: Direction):
        self.floor = floor
        self.direction = direction
    def __lt__(self, other): return self.floor < other.floor

class Elevator:
    def __init__(self, id: int, capacity: int = 10):
        self.id = id
        self.capacity = capacity
        self.current_floor = 0
        self.direction = Direction.IDLE
        self.state = ElevatorState.STOPPED
        self.door_state = DoorState.CLOSED
        self._requests: List[int] = []
    
    def add_request(self, floor: int):
        if floor not in self._requests:
            self._requests.append(floor)
            self._requests.sort()
    
    def move(self):
        if not self._requests:
            self.direction = Direction.IDLE
            return
        next_floor = self._requests[0] if self.direction != Direction.DOWN else self._requests[-1]
        if next_floor > self.current_floor:
            self.direction = Direction.UP
            self.current_floor += 1
        elif next_floor < self.current_floor:
            self.direction = Direction.DOWN
            self.current_floor -= 1
        
        if self.current_floor in self._requests:
            self._requests.remove(self.current_floor)
            self.open_door()
    
    def open_door(self): 
        self.door_state = DoorState.OPEN
        print(f"Elevator {self.id} at floor {self.current_floor}, doors open")
    
    def close_door(self): self.door_state = DoorState.CLOSED
    
    def __str__(self): return f"Elevator {self.id}: Floor {self.current_floor}, {self.direction.name}"

class ElevatorSystem:
    _instance = None
    
    def __new__(cls, num_elevators: int = 4, num_floors: int = 20):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.elevators = {i: Elevator(i) for i in range(num_elevators)}
            cls._instance.num_floors = num_floors
        return cls._instance
    
    def request_elevator(self, floor: int, direction: Direction = Direction.UP):
        # Find nearest available elevator
        best = min(self.elevators.values(), 
                   key=lambda e: abs(e.current_floor - floor))
        best.add_request(floor)
        return best
    
    def step(self):
        for elevator in self.elevators.values():
            elevator.move()
