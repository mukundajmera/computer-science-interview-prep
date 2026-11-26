"""
Elevator System - v1 Basic Implementation
"""

from enum import Enum
from typing import List, Optional
import time


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"


class ElevatorState(Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    DOOR_OPEN = "DOOR_OPEN"


class Elevator:
    def __init__(self, elevator_id: int, min_floor: int = 0, max_floor: int = 10):
        self.elevator_id = elevator_id
        self.current_floor = 0
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.requests: List[int] = []
    
    def add_request(self, floor: int) -> bool:
        if floor < self.min_floor or floor > self.max_floor:
            return False
        if floor not in self.requests:
            self.requests.append(floor)
            self.requests.sort()
        return True
    
    def move(self) -> None:
        if not self.requests:
            self.direction = Direction.IDLE
            self.state = ElevatorState.IDLE
            return
        
        target = self.requests[0]
        if target > self.current_floor:
            self.direction = Direction.UP
            self.current_floor += 1
        elif target < self.current_floor:
            self.direction = Direction.DOWN
            self.current_floor -= 1
        
        self.state = ElevatorState.MOVING
        print(f"Elevator {self.elevator_id} at floor {self.current_floor}")
        
        if self.current_floor == target:
            self.open_doors()
            self.requests.pop(0)
    
    def open_doors(self) -> None:
        self.state = ElevatorState.DOOR_OPEN
        print(f"Elevator {self.elevator_id} doors open at floor {self.current_floor}")
    
    def close_doors(self) -> None:
        self.state = ElevatorState.IDLE
        print(f"Elevator {self.elevator_id} doors closed")


class ElevatorController:
    def __init__(self, num_elevators: int, max_floor: int = 10):
        self.elevators = [Elevator(i, 0, max_floor) for i in range(num_elevators)]
        self.max_floor = max_floor
    
    def request_elevator(self, floor: int, direction: Direction) -> Optional[Elevator]:
        best = None
        min_distance = float('inf')
        
        for elevator in self.elevators:
            distance = abs(elevator.current_floor - floor)
            if distance < min_distance:
                min_distance = distance
                best = elevator
        
        if best:
            best.add_request(floor)
            print(f"Elevator {best.elevator_id} assigned to floor {floor}")
        return best
    
    def step(self) -> None:
        for elevator in self.elevators:
            elevator.move()


def main():
    print("=== Elevator System v1 - Basic Demo ===\n")
    
    controller = ElevatorController(2, 10)
    
    controller.request_elevator(5, Direction.UP)
    controller.request_elevator(3, Direction.DOWN)
    
    for _ in range(10):
        controller.step()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
