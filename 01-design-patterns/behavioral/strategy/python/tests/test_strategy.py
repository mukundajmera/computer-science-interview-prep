"""
Strategy Pattern - Unit Tests
"""
import unittest
from typing import Callable


class TestStrategyPattern(unittest.TestCase):
    
    def test_strategy_switching(self):
        """Test that strategies can be swapped at runtime"""
        add = lambda a, b: a + b
        subtract = lambda a, b: a - b
        multiply = lambda a, b: a * b
        
        class Calculator:
            def __init__(self):
                self.strategy: Callable[[int, int], int] = add
            
            def set_strategy(self, strategy):
                self.strategy = strategy
            
            def execute(self, a: int, b: int) -> int:
                return self.strategy(a, b)
        
        calc = Calculator()
        
        self.assertEqual(calc.execute(5, 3), 8)
        
        calc.set_strategy(subtract)
        self.assertEqual(calc.execute(5, 3), 2)
        
        calc.set_strategy(multiply)
        self.assertEqual(calc.execute(5, 3), 15)
    
    def test_discount_strategies(self):
        """Test discount calculation strategies"""
        percentage_off = lambda pct: lambda price: price * (1 - pct / 100)
        fixed_off = lambda amt: lambda price: max(0, price - amt)
        
        ten_percent = percentage_off(10)
        five_dollars = fixed_off(5)
        
        self.assertAlmostEqual(ten_percent(100), 90.0)
        self.assertAlmostEqual(five_dollars(100), 95.0)
        self.assertAlmostEqual(five_dollars(3), 0.0)  # Can't go negative
    
    def test_null_strategy_protection(self):
        """Test handling of missing strategy"""
        class Context:
            def __init__(self):
                self.strategy = None
            
            def execute(self):
                if self.strategy is None:
                    raise RuntimeError("Strategy not set")
                return self.strategy()
        
        ctx = Context()
        with self.assertRaises(RuntimeError):
            ctx.execute()
        
        ctx.strategy = lambda: "success"
        self.assertEqual(ctx.execute(), "success")
    
    def test_strategy_composition(self):
        """Test composing multiple strategies"""
        from functools import reduce
        
        strategies = [
            lambda x: x * 0.9,  # 10% off
            lambda x: x - 5,    # $5 off
        ]
        
        def compose(price):
            return reduce(lambda p, fn: fn(p), strategies, price)
        
        result = compose(100)
        self.assertAlmostEqual(result, 85.0)  # 100 → 90 → 85
    
    def test_sorting_strategies(self):
        """Test sorting strategy produces correct results"""
        data = [3, 1, 4, 1, 5, 9, 2, 6]
        expected = [1, 1, 2, 3, 4, 5, 6, 9]
        
        # Different "strategies" should produce same result
        builtin_sort = sorted
        reverse_twice = lambda x: list(reversed(sorted(x, reverse=True)))
        
        self.assertEqual(builtin_sort(data), expected)
        self.assertEqual(reverse_twice(data), expected)
    
    def test_strategy_independence(self):
        """Test that strategies don't affect each other"""
        class ImmutableContext:
            def __init__(self, strategy):
                self._strategy = strategy
            
            def execute(self, value):
                return self._strategy(value)
        
        ctx1 = ImmutableContext(lambda x: x * 2)
        ctx2 = ImmutableContext(lambda x: x + 10)
        
        self.assertEqual(ctx1.execute(5), 10)
        self.assertEqual(ctx2.execute(5), 15)
        # Verify ctx1 wasn't affected by ctx2
        self.assertEqual(ctx1.execute(5), 10)


if __name__ == "__main__":
    unittest.main()
