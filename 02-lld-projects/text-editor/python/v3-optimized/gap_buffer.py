from typing import List

class GapBuffer:
    def __init__(self, initial_capacity: int = 10):
        self.buffer: List[str] = [''] * initial_capacity
        self.gap_start = 0
        self.gap_end = initial_capacity
        self.capacity = initial_capacity

    def _resize(self) -> None:
        new_capacity = self.capacity * 2
        new_buffer = [''] * new_capacity
        
        # Copy elements before gap
        for i in range(self.gap_start):
            new_buffer[i] = self.buffer[i]
            
        # Copy elements after gap
        elements_after_gap = self.capacity - self.gap_end
        new_gap_end = new_capacity - elements_after_gap
        for i in range(elements_after_gap):
            new_buffer[new_gap_end + i] = self.buffer[self.gap_end + i]
            
        self.buffer = new_buffer
        self.gap_end = new_gap_end
        self.capacity = new_capacity

    def _move_gap(self, index: int) -> None:
        if index < self.gap_start:
            # Move gap left
            shift_amount = self.gap_start - index
            for i in range(shift_amount):
                self.gap_start -= 1
                self.gap_end -= 1
                self.buffer[self.gap_end] = self.buffer[self.gap_start]
                self.buffer[self.gap_start] = ''
        elif index > self.gap_start:
            # Move gap right
            shift_amount = index - self.gap_start
            for i in range(shift_amount):
                self.buffer[self.gap_start] = self.buffer[self.gap_end]
                self.buffer[self.gap_end] = ''
                self.gap_start += 1
                self.gap_end += 1

    def insert(self, index: int, text: str) -> None:
        if self.gap_start == self.gap_end:
            self._resize()
        
        # Determine actual insertion point
        logical_length = self.capacity - (self.gap_end - self.gap_start)
        actual_index = min(index, logical_length)
        actual_index = max(0, actual_index)
        
        self._move_gap(actual_index)
        
        self.buffer[self.gap_start] = text
        self.gap_start += 1

    def delete(self, index: int) -> None:
        logical_length = self.capacity - (self.gap_end - self.gap_start)
        if index < 0 or index >= logical_length:
            return
            
        # To delete an element, we move the gap right after it, then expand the gap left
        self._move_gap(index + 1)
        self.gap_start -= 1
        self.buffer[self.gap_start] = ''

    def get_all(self) -> List[str]:
        result = []
        for i in range(self.gap_start):
            result.append(self.buffer[i])
        for i in range(self.gap_end, self.capacity):
            result.append(self.buffer[i])
        return result
        
    def replace(self, index: int, text: str) -> None:
        logical_length = self.capacity - (self.gap_end - self.gap_start)
        if index < 0 or index >= logical_length:
            return
            
        # Find the physical index
        if index < self.gap_start:
            physical_index = index
        else:
            physical_index = index + (self.gap_end - self.gap_start)
            
        self.buffer[physical_index] = text
