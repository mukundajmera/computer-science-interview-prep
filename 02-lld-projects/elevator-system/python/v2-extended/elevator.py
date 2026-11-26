"""Elevator System Python Module - v2 Extended with State Pattern."""
from enum import Enum
from typing import Dict, List
from abc import ABC, abstractmethod

class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"

class DoorState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    OBSTRUCTED = "OBSTRUCTED"

class Request:
    def __init__(self, floor: int, direction: Direction):
        self.floor = floor
        self.direction = direction
    def __lt__(self, other): return self.floor < other.floor

class ElevatorState(ABC):
    @abstractmethod
    def handle_request(self, elevator, floor: int):
        pass

    @abstractmethod
    def move(self, elevator):
        pass

class IdleState(ElevatorState):
    def handle_request(self, elevator, floor: int):
        if floor not in elevator._requests:
            elevator._requests.append(floor)
            elevator._requests.sort()
        elevator.set_state(MovingState())

    def move(self, elevator):
        pass

class MovingState(ElevatorState):
    def handle_request(self, elevator, floor: int):
        if floor not in elevator._requests:
            elevator._requests.append(floor)
            elevator._requests.sort()

    def move(self, elevator):
        if not elevator._requests:
            elevator.direction = Direction.IDLE
            elevator.set_state(IdleState())
            return
            
        next_floor = elevator._requests[0] if elevator.direction != Direction.DOWN else elevator._requests[-1]
        
        if next_floor > elevator.current_floor:
            elevator.direction = Direction.UP
            elevator.current_floor += 1
        elif next_floor < elevator.current_floor:
            elevator.direction = Direction.DOWN
            elevator.current_floor -= 1
        
        if elevator.current_floor in elevator._requests:
            elevator.set_state(StoppedState())
            # In StoppedState, we'll open doors and remove the request

class StoppedState(ElevatorState):
    def handle_request(self, elevator, floor: int):
        if floor not in elevator._requests:
            elevator._requests.append(floor)
            elevator._requests.sort()

    def move(self, elevator):
        # We process the stop
        if elevator.current_floor in elevator._requests:
            elevator._requests.remove(elevator.current_floor)
        elevator.open_door()
        # After stopping and opening doors, we transition back to Moving if requests remain, or Idle
        if elevator._requests:
            elevator.set_state(MovingState())
        else:
            elevator.direction = Direction.IDLE
            elevator.set_state(IdleState())

class Elevator:
    def __init__(self, id: int, capacity: int = 10):
        self.id = id
        self.capacity = capacity
        self.current_floor = 0
        self.direction = Direction.IDLE
        self.door_state = DoorState.CLOSED
        self._requests: List[int] = []
        self._state: ElevatorState = IdleState()
        
    def set_state(self, state: ElevatorState):
        self._state = state
    
    def add_request(self, floor: int):
        self._state.handle_request(self, floor)
    
    def move(self):
        # Pre-check door sensor before moving
        if self.door_state == DoorState.OBSTRUCTED:
            print(f"Elevator {self.id} doors are obstructed. Cannot move.")
            return
        # Auto-close doors if open
        if self.door_state == DoorState.OPEN:
            self.close_door()
            
        self._state.move(self)
    
    def open_door(self):
        self.door_state = DoorState.OPEN
        print(f"Elevator {self.id} at floor {self.current_floor}, doors open")
        
    def close_door(self):
        # Check sensor here as an example
        if self.check_door_sensor():
            self.door_state = DoorState.OBSTRUCTED
            print(f"Elevator {self.id} door obstructed!")
        else:
            self.door_state = DoorState.CLOSED
            
    def check_door_sensor(self) -> bool:
        # Simulate sensor (False = no obstruction)
        return False
        
    def trigger_obstruction(self):
        self.door_state = DoorState.OBSTRUCTED
        print(f"Elevator {self.id} door sensor triggered!")

    def clear_obstruction(self):
        self.door_state = DoorState.OPEN
        print(f"Elevator {self.id} obstruction cleared, doors open.")
    
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
