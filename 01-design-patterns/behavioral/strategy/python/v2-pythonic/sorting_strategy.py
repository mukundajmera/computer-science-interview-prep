"""
Strategy Pattern - V2 Pythonic: Using First-Class Functions

Python's first-class functions make Strategy pattern more elegant.
"""
from typing import Callable, List, TypeVar
import time

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


T = TypeVar('T')
SortStrategy = Callable[[List[int]], List[int]]


# Strategy functions (instead of classes)
def bubble_sort(data: List[int]) -> List[int]:
    """Simple bubble sort - O(n²)"""
    arr = data.copy()
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def quick_sort(data: List[int]) -> List[int]:
    """Quick sort - O(n log n) average"""
    if len(data) <= 1:
        return data.copy()
    
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(data: List[int]) -> List[int]:
    """Merge sort - O(n log n) stable"""
    if len(data) <= 1:
        return data.copy()
    
    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# Lambda-based strategies
reverse_sort: SortStrategy = lambda data: sorted(data, reverse=True)
absolute_sort: SortStrategy = lambda data: sorted(data, key=abs)


# Context using function strategy
class SmartSorter:
    def __init__(self, strategy: SortStrategy = None):
        self._strategy = strategy or sorted  # Default to built-in
    
    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy
        print(f"Strategy set to: {strategy.__name__ if hasattr(strategy, '__name__') else 'lambda'}")
    
    def auto_select(self, data_size: int) -> None:
        """Auto-select based on data characteristics"""
        if data_size < 10:
            self._strategy = bubble_sort
        elif data_size < 1000:
            self._strategy = quick_sort
        else:
            self._strategy = merge_sort
        print(f"Auto-selected: {self._strategy.__name__}")
    
    def sort(self, data: List[int]) -> List[int]:
        start = time.perf_counter()
        result = self._strategy(data)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"Sorted in {elapsed:.3f}ms")
        return result


# Strategy factory using dictionary
SORT_STRATEGIES = {
    "bubble": bubble_sort,
    "quick": quick_sort,
    "merge": merge_sort,
    "builtin": sorted,
    "reverse": reverse_sort,
}


def get_strategy(name: str) -> SortStrategy:
    """Factory function to get strategy by name"""
    if name not in SORT_STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}")
    return SORT_STRATEGIES[name]


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90, 5, 77, 30]
    print(f"Original: {data}\n")
    
    sorter = SmartSorter()
    
    # Using different strategies
    print("=== Bubble Sort ===")
    sorter.set_strategy(bubble_sort)
    print(f"Result: {sorter.sort(data)}")
    
    print("\n=== Quick Sort ===")
    sorter.set_strategy(quick_sort)
    print(f"Result: {sorter.sort(data)}")
    
    print("\n=== Merge Sort ===")
    sorter.set_strategy(merge_sort)
    print(f"Result: {sorter.sort(data)}")
    
    # Using factory
    print("\n=== Strategy Factory ===")
    for name in ["bubble", "quick", "merge"]:
        strategy = get_strategy(name)
        result = strategy(data)
        print(f"{name}: {result}")
    
    # Auto-selection
    print("\n=== Auto-Selection ===")
    sorter.auto_select(len(data))
    sorter.sort(data)
    
    # Lambda strategy
    print("\n=== Lambda Strategy ===")
    sorter.set_strategy(lambda x: sorted(x, reverse=True))
    print(f"Reverse: {sorter.sort(data)}")
