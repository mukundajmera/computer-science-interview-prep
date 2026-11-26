import threading
from enum import Enum
from typing import Dict, List, Optional
import time

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
        self.lock = threading.Lock()
    
    def add_request(self, floor: int):
        with self.lock:
            if floor not in self._requests:
                self._requests.append(floor)
                self._requests.sort()
    
    def move(self):
        with self.lock:
            if not self._requests:
                self.direction = Direction.IDLE
                return
                
            # Implementing SCAN algorithm logic within elevator move
            if self.direction == Direction.UP:
                next_floors = [f for f in self._requests if f >= self.current_floor]
                if not next_floors:
                    self.direction = Direction.DOWN
                    next_floors = [f for f in self._requests if f < self.current_floor]
                    if not next_floors:
                        self.direction = Direction.IDLE
                        return
                    next_floor = max(next_floors)
                else:
                    next_floor = min(next_floors)
            elif self.direction == Direction.DOWN:
                next_floors = [f for f in self._requests if f <= self.current_floor]
                if not next_floors:
                    self.direction = Direction.UP
                    next_floors = [f for f in self._requests if f > self.current_floor]
                    if not next_floors:
                        self.direction = Direction.IDLE
                        return
                    next_floor = min(next_floors)
                else:
                    next_floor = max(next_floors)
            else:
                # IDLE, pick nearest
                next_floor = min(self._requests, key=lambda f: abs(f - self.current_floor))
                if next_floor > self.current_floor:
                    self.direction = Direction.UP
                elif next_floor < self.current_floor:
                    self.direction = Direction.DOWN
            
            if next_floor > self.current_floor:
                self.current_floor += 1
                self.direction = Direction.UP
            elif next_floor < self.current_floor:
                self.current_floor -= 1
                self.direction = Direction.DOWN
            
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
    _lock = threading.Lock()
    
    def __new__(cls, num_elevators: int = 4, num_floors: int = 20):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.elevators = {i: Elevator(i) for i in range(num_elevators)}
                cls._instance.num_floors = num_floors
            return cls._instance
            
    def get_best_elevator(self, floor: int, direction: Direction) -> Elevator:
        best_elevator = None
        min_distance = float('inf')
        
        for elevator in self.elevators.values():
            with elevator.lock:
                distance = abs(elevator.current_floor - floor)
                
                # Penalty if elevator is moving in opposite direction
                if elevator.direction != Direction.IDLE and elevator.direction != direction:
                    if elevator.direction == Direction.UP and floor < elevator.current_floor:
                        distance += self.num_floors
                    elif elevator.direction == Direction.DOWN and floor > elevator.current_floor:
                        distance += self.num_floors
                        
                if distance < min_distance:
                    min_distance = distance
                    best_elevator = elevator
                    
        return best_elevator if best_elevator else self.elevators[0]
    
    def request_elevator(self, floor: int, direction: Direction = Direction.UP):
        # Multiple elevator bank dispatcher
        best = self.get_best_elevator(floor, direction)
        best.add_request(floor)
        return best
    
    def step(self):
        for elevator in self.elevators.values():
            elevator.move()
