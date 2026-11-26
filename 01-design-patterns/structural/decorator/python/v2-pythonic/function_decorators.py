"""
Decorator Pattern - V2 Pythonic: Using Python's @decorator syntax

Demonstrates the connection between GoF Decorator pattern and
Python's built-in decorator syntax for functions.
"""
from functools import wraps
from typing import Callable
import time


# ============ Function Decorators (Pythonic) ============

def logged(func: Callable) -> Callable:
    """Decorator that logs function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned {result}")
        return result
    return wrapper


def timed(func: Callable) -> Callable:
    """Decorator that measures execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[TIME] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def cached(func: Callable) -> Callable:
    """Decorator that caches results"""
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            print(f"[CACHE] Hit for {args}")
            return cache[args]
        print(f"[CACHE] Miss for {args}")
        result = func(*args)
        cache[args] = result
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator factory that retries on failure"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[RETRY] Attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected retry failure")
        return wrapper
    return decorator


def validate_types(*type_args, **type_kwargs):
    """Decorator that validates argument types"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i, (arg, expected_type) in enumerate(zip(args, type_args)):
                if not isinstance(arg, expected_type):
                    raise TypeError(
                        f"Argument {i} must be {expected_type.__name__}, "
                        f"got {type(arg).__name__}"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============ Class-based Decorators ============

class CountCalls:
    """Class-based decorator that counts function calls"""
    
    def __init__(self, func: Callable):
        self.func = func
        self.count = 0
        wraps(func)(self)
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"[COUNT] {self.func.__name__} called {self.count} times")
        return self.func(*args, **kwargs)


class Deprecated:
    """Class-based decorator that marks functions as deprecated"""
    
    def __init__(self, message: str = ""):
        self.message = message
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            msg = f"{func.__name__} is deprecated. {self.message}"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper


# ============ Example Usage ============

@logged
@timed
def slow_operation(n: int) -> int:
    """A slow operation"""
    time.sleep(0.1)
    return n * 2


@cached
def fibonacci(n: int) -> int:
    """Compute fibonacci recursively with caching"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@CountCalls
def greet(name: str) -> str:
    return f"Hello, {name}!"


@validate_types(str, int)
def repeat_string(s: str, times: int) -> str:
    return s * times


# Stacking multiple decorators
@logged
@timed
@cached
def complex_calculation(x: int, y: int) -> int:
    """Function with multiple decorators stacked"""
    time.sleep(0.05)
    return x ** y


# Demo
if __name__ == "__main__":
    print("=== Logged + Timed Decorator ===")
    result = slow_operation(5)
    print(f"Result: {result}")
    
    print("\n=== Cached Decorator (Fibonacci) ===")
    print(f"fib(10) = {fibonacci(10)}")
    print(f"fib(10) again = {fibonacci(10)}")  # Cached
    
    print("\n=== Count Calls Decorator ===")
    greet("Alice")
    greet("Bob")
    greet("Charlie")
    
    print("\n=== Type Validation Decorator ===")
    print(repeat_string("Hi! ", 3))
    try:
        repeat_string(123, "three")  # Should fail
    except TypeError as e:
        print(f"Caught error: {e}")
    
    print("\n=== Stacked Decorators ===")
    print(f"2^10 = {complex_calculation(2, 10)}")
    print(f"2^10 again = {complex_calculation(2, 10)}")  # Cached
