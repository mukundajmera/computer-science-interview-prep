from typing import TypeVar, Generic, Callable, Any, Dict, List, Tuple
from dataclasses import dataclass

T = TypeVar('T')
A = TypeVar('A')
R = TypeVar('R')

@dataclass
class WindowResult(Generic[R]):
    start: int
    end: int
    result: R

    def __str__(self):
        return f"Window[{self.start}-{self.end}]: {self.result}"

class SlidingWindowAggregator(Generic[T, A, R]):
    def __init__(
        self,
        window_size: int,
        slide_size: int,
        allowed_lateness: int,
        timestamp_extractor: Callable[[T], int],
        create_accumulator: Callable[[], A],
        add_fn: Callable[[T, A], A],
        get_result_fn: Callable[[A], R]
    ):
        if window_size <= 0 or slide_size <= 0:
            raise ValueError("Window and slide sizes must be positive")

        self.window_size = window_size
        self.slide_size = slide_size
        self.allowed_lateness = allowed_lateness
        self.timestamp_extractor = timestamp_extractor
        self.create_accumulator = create_accumulator
        self.add_fn = add_fn
        self.get_result_fn = get_result_fn

        self.window_states: Dict[int, A] = {}
        self.current_watermark = -float('inf')

    def process_event(self, event: T) -> None:
        timestamp = self.timestamp_extractor(event)

        if timestamp < self.current_watermark - self.allowed_lateness:
            return  # Discard late event

        last_window_start = (timestamp // self.slide_size) * self.slide_size

        start = last_window_start
        while start > timestamp - self.window_size:
            window_end = start + self.window_size
            if self.current_watermark < window_end + self.allowed_lateness:
                if start not in self.window_states:
                    self.window_states[start] = self.create_accumulator()
                self.window_states[start] = self.add_fn(event, self.window_states[start])
            start -= self.slide_size

    def advance_watermark(self, new_watermark: int) -> List[WindowResult[R]]:
        results = []
        if new_watermark > self.current_watermark:
            self.current_watermark = new_watermark

            # Use list of keys to allow modifying the dictionary during iteration
            for window_start in list(self.window_states.keys()):
                window_end = window_start + self.window_size

                if self.current_watermark >= window_end + self.allowed_lateness:
                    result = self.get_result_fn(self.window_states[window_start])
                    results.append(WindowResult(window_start, window_end, result))
                    del self.window_states[window_start]

        return sorted(results, key=lambda x: x.start)

    @property
    def get_current_watermark(self) -> int:
        return self.current_watermark

# Built-in aggregations
def count_aggregation() -> Tuple[Callable[[], List[int]], Callable[[Any, List[int]], List[int]], Callable[[List[int]], int]]:
    def create() -> List[int]:
        return [0]

    def add(val: Any, acc: List[int]) -> List[int]:
        acc[0] += 1
        return acc

    def get_res(acc: List[int]) -> int:
        return acc[0]

    return create, add, get_res

def sum_aggregation() -> Tuple[Callable[[], List[float]], Callable[[Any, List[float]], List[float]], Callable[[List[float]], float]]:
    def create() -> List[float]:
        return [0.0]

    def add(val: Any, acc: List[float]) -> List[float]:
        if hasattr(val, 'value'):
            acc[0] += float(val.value)
        else:
            acc[0] += float(val)
        return acc

    def get_res(acc: List[float]) -> float:
        return acc[0]

    return create, add, get_res
