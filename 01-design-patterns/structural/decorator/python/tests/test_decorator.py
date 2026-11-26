"""
Tests for Decorator Pattern implementations
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-pythonic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-advanced'))


class TestV1CoffeeShop(unittest.TestCase):
    """Tests for V1 Basic Coffee Shop"""
    
    def test_espresso_base_cost(self):
        """Espresso should have base cost"""
        from coffee_shop import Espresso
        
        espresso = Espresso()
        
        self.assertAlmostEqual(espresso.cost(), 1.99, places=2)
        self.assertEqual(espresso.description, "Espresso")
    
    def test_single_decorator(self):
        """Single decorator should add cost and description"""
        from coffee_shop import Espresso, Milk
        
        beverage = Milk(Espresso())
        
        self.assertAlmostEqual(beverage.cost(), 2.29, places=2)
        self.assertIn("Milk", beverage.description)
    
    def test_stacked_decorators(self):
        """Multiple decorators should stack correctly"""
        from coffee_shop import DarkRoast, Mocha, Whip
        
        beverage = DarkRoast()  # 1.49
        beverage = Mocha(beverage)  # +0.50
        beverage = Mocha(beverage)  # +0.50
        beverage = Whip(beverage)   # +0.40
        
        self.assertAlmostEqual(beverage.cost(), 2.89, places=2)
        self.assertIn("Dark Roast", beverage.description)
        # Should have Mocha twice
        self.assertEqual(beverage.description.count("Mocha"), 2)
    
    def test_decorator_order_independence(self):
        """Order of decorators should not affect total cost"""
        from coffee_shop import Espresso, Milk, Mocha
        
        order1 = Mocha(Milk(Espresso()))
        order2 = Milk(Mocha(Espresso()))
        
        self.assertAlmostEqual(order1.cost(), order2.cost(), places=2)


class TestV2FunctionDecorators(unittest.TestCase):
    """Tests for V2 Pythonic Function Decorators"""
    
    def test_cached_decorator(self):
        """Cached decorator should cache results"""
        from function_decorators import cached
        
        call_count = 0
        
        @cached
        def expensive_func(n):
            nonlocal call_count
            call_count += 1
            return n * 2
        
        # First call
        result1 = expensive_func(5)
        # Second call - should be cached
        result2 = expensive_func(5)
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Only called once
    
    def test_validate_types_decorator(self):
        """Type validation decorator should raise on wrong types"""
        from function_decorators import validate_types
        
        @validate_types(str, int)
        def repeat(s, times):
            return s * times
        
        # Valid types
        result = repeat("Hi", 3)
        self.assertEqual(result, "HiHiHi")
        
        # Invalid types
        with self.assertRaises(TypeError):
            repeat(123, "three")
    
    def test_count_calls_decorator(self):
        """CountCalls decorator should count calls"""
        from function_decorators import CountCalls
        
        @CountCalls
        def my_func():
            return "result"
        
        my_func()
        my_func()
        my_func()
        
        self.assertEqual(my_func.count, 3)


class TestV3Middleware(unittest.TestCase):
    """Tests for V3 Advanced Middleware"""
    
    def test_application_handler(self):
        """Application handler should return correct response"""
        from middleware import ApplicationHandler, HttpRequest
        
        handler = ApplicationHandler()
        request = HttpRequest("GET", "/api/users")
        
        response = handler.handle(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.body)
    
    def test_authentication_middleware(self):
        """Authentication middleware should set user attribute"""
        from middleware import AuthenticationMiddleware, ApplicationHandler, HttpRequest
        
        handler = AuthenticationMiddleware(ApplicationHandler())
        request = HttpRequest("GET", "/api/protected")
        request.headers["Authorization"] = "Bearer valid-token-123"
        
        handler.handle(request)
        
        self.assertEqual(request.get_attribute("user"), "AuthenticatedUser")
    
    def test_rate_limit_middleware(self):
        """Rate limit middleware should block after max requests"""
        from middleware import RateLimitMiddleware, ApplicationHandler, HttpRequest
        
        handler = RateLimitMiddleware(ApplicationHandler(), max_requests=3)
        
        # First 3 requests should succeed
        for i in range(3):
            request = HttpRequest("GET", "/api/users")
            request.headers["X-Client-IP"] = "192.168.1.100"
            response = handler.handle(request)
            self.assertEqual(response.status_code, 200)
        
        # 4th request should be rate limited
        request = HttpRequest("GET", "/api/users")
        request.headers["X-Client-IP"] = "192.168.1.100"
        response = handler.handle(request)
        self.assertEqual(response.status_code, 429)
    
    def test_caching_middleware(self):
        """Caching middleware should cache GET requests"""
        from middleware import CachingMiddleware, ApplicationHandler, HttpRequest
        
        handler = CachingMiddleware(ApplicationHandler())
        
        # First request - cache miss
        req1 = HttpRequest("GET", "/api/users")
        res1 = handler.handle(req1)
        self.assertEqual(res1.headers.get("X-Cache"), "MISS")
        
        # Second request - cache hit
        req2 = HttpRequest("GET", "/api/users")
        res2 = handler.handle(req2)
        self.assertEqual(res2.headers.get("X-Cache"), "HIT")
    
    def test_middleware_stack(self):
        """Full middleware stack should work together"""
        from middleware import create_middleware_stack, ApplicationHandler, HttpRequest
        
        handler = create_middleware_stack(ApplicationHandler())
        
        request = HttpRequest("GET", "/api/protected")
        request.headers["Authorization"] = "Bearer valid-token-123"
        request.headers["X-Client-IP"] = "192.168.1.1"
        
        response = handler.handle(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome", response.body)


if __name__ == "__main__":
    unittest.main()
