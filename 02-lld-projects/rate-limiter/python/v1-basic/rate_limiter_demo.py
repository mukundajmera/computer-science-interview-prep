"""
Rate Limiter - V1 Basic Demo

Demonstrates the Token Bucket rate limiter in action.
"""
import time
from rate_limit_config import RateLimitConfig
from rate_limiter import RateLimiter


def main():
    print("=== Rate Limiter Demo (Token Bucket) ===\n")
    
    # Create rate limiter: 5 requests per second
    config = RateLimitConfig.per_second(5)
    limiter = RateLimiter(config)
    
    client_id = "user123"
    
    # Test 1: Burst of requests
    print("Test 1: Sending 7 requests rapidly...")
    for i in range(1, 8):
        result = limiter.allow_request(client_id)
        status = "ALLOWED" if result.allowed else "REJECTED"
        print(f"  Request {i}: {status} (remaining: {result.remaining_tokens})")
    
    # Test 2: Wait for token refill
    print("\nTest 2: Waiting 500ms for refill...")
    time.sleep(0.5)
    
    result = limiter.allow_request(client_id)
    status = "ALLOWED" if result.allowed else "REJECTED"
    print(f"  Request after wait: {status} (remaining: {result.remaining_tokens})")
    
    # Test 3: Different client
    print("\nTest 3: Different client 'user456'...")
    other_client = "user456"
    for i in range(1, 4):
        result = limiter.allow_request(other_client)
        status = "ALLOWED" if result.allowed else "REJECTED"
        print(f"  Request {i}: {status} (remaining: {result.remaining_tokens})")
    
    # Test 4: Reset client
    print("\nTest 4: Resetting 'user123'...")
    limiter.reset_client(client_id)
    result = limiter.allow_request(client_id)
    status = "ALLOWED" if result.allowed else "REJECTED"
    print(f"  Request after reset: {status} (remaining: {result.remaining_tokens})")
    
    print(f"\n=== Demo Complete ===")
    print(f"Tracked clients: {limiter.client_count}")


if __name__ == "__main__":
    main()
