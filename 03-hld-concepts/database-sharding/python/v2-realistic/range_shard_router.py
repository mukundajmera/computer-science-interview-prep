"""
Range-based sharding with dynamic shard configuration.
More realistic implementation with range definitions and routing.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from bisect import bisect_left


@dataclass
class ShardConfig:
    """Configuration for a single shard."""
    shard_id: str
    start_range: int
    end_range: int
    is_healthy: bool = True

    def contains(self, value: int) -> bool:
        """Check if value falls within this shard's range."""
        return self.start_range <= value < self.end_range


@dataclass
class ShardDatabase:
    """Simple in-memory shard database."""
    shard_id: str
    data: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    def put(self, key: int, value: Dict[str, Any]) -> None:
        """Store data in this shard."""
        self.data[key] = value

    def get(self, key: int) -> Optional[Dict[str, Any]]:
        """Retrieve data from this shard."""
        return self.data.get(key)

    def range_query(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Get all items within a key range."""
        return [
            value for key, value in self.data.items()
            if start <= key < end
        ]

    def size(self) -> int:
        """Get number of items in this shard."""
        return len(self.data)


class RangeShardRouter:
    """Range-based shard router with health checking."""

    def __init__(self):
        """Initialize the router."""
        self.shard_ranges: List[Tuple[int, ShardConfig]] = []
        self.shards: Dict[str, ShardDatabase] = {}

    def add_shard(self, shard_id: str, start_range: int, end_range: int) -> None:
        """Add a shard with its range configuration.
        
        Args:
            shard_id: Unique identifier for the shard
            start_range: Start of key range (inclusive)
            end_range: End of key range (exclusive)
        """
        config = ShardConfig(shard_id, start_range, end_range)
        
        # Keep ranges sorted by start
        self.shard_ranges.append((start_range, config))
        self.shard_ranges.sort(key=lambda x: x[0])
        
        self.shards[shard_id] = ShardDatabase(shard_id)

    def route_to_shard(self, key: int) -> ShardConfig:
        """Route a key to its shard.
        
        Args:
            key: The key to route
            
        Returns:
            ShardConfig for the appropriate shard
            
        Raises:
            ValueError: If no shard covers this key
        """
        for start, config in self.shard_ranges:
            if config.contains(key):
                return config
        raise ValueError(f"No shard found for key: {key}")

    def put(self, key: int, value: Dict[str, Any]) -> None:
        """Store data in appropriate shard.
        
        Args:
            key: Data key (also used for routing)
            value: Data to store
            
        Raises:
            RuntimeError: If target shard is unhealthy
        """
        config = self.route_to_shard(key)
        if not config.is_healthy:
            raise RuntimeError(f"Shard {config.shard_id} is unhealthy")
        self.shards[config.shard_id].put(key, value)

    def get(self, key: int) -> Optional[Dict[str, Any]]:
        """Retrieve data from appropriate shard.
        
        Args:
            key: Data key (also used for routing)
            
        Returns:
            Stored data or None if not found
        """
        config = self.route_to_shard(key)
        return self.shards[config.shard_id].get(key)

    def range_query(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Execute range query across relevant shards.
        
        Args:
            start: Start of range (inclusive)
            end: End of range (exclusive)
            
        Returns:
            List of matching records
        """
        results = []
        
        for _, config in self.shard_ranges:
            # Check if shard range overlaps with query range
            if config.start_range < end and config.end_range > start:
                shard = self.shards[config.shard_id]
                results.extend(shard.range_query(start, end))
        
        return results

    def mark_shard_unhealthy(self, shard_id: str) -> None:
        """Mark a shard as unhealthy."""
        for _, config in self.shard_ranges:
            if config.shard_id == shard_id:
                config.is_healthy = False
                break

    def mark_shard_healthy(self, shard_id: str) -> None:
        """Mark a shard as healthy."""
        for _, config in self.shard_ranges:
            if config.shard_id == shard_id:
                config.is_healthy = True
                break

    def print_distribution(self) -> None:
        """Print shard distribution."""
        print("=== Shard Distribution ===")
        for _, config in self.shard_ranges:
            shard = self.shards[config.shard_id]
            status = "healthy" if config.is_healthy else "unhealthy"
            print(f"Shard {config.shard_id} [{config.start_range}-{config.end_range}): "
                  f"{shard.size()} items ({status})")

    def get_shard_count(self) -> int:
        """Get number of shards."""
        return len(self.shards)


def main():
    """Demo for range-based sharding."""
    print("=== Range-Based Sharding Demo ===\n")

    router = RangeShardRouter()

    # Configure shards with ranges
    print("Configuring shards with ranges...")
    router.add_shard("shard_1", 0, 1_000_000)
    router.add_shard("shard_2", 1_000_000, 2_000_000)
    router.add_shard("shard_3", 2_000_000, 3_000_000)
    router.add_shard("shard_4", 3_000_000, 4_000_000)

    print("Shard 1: user_id 0 - 999,999")
    print("Shard 2: user_id 1,000,000 - 1,999,999")
    print("Shard 3: user_id 2,000,000 - 2,999,999")
    print("Shard 4: user_id 3,000,000 - 3,999,999\n")

    # Insert user data
    print("Inserting users...")
    user_ids = [100, 500_000, 1_500_000, 2_100_000, 3_500_000]
    
    for user_id in user_ids:
        user_data = {
            "user_id": user_id,
            "name": f"User_{user_id}",
            "email": f"user{user_id}@example.com"
        }
        router.put(user_id, user_data)
        config = router.route_to_shard(user_id)
        print(f"User {user_id} -> {config.shard_id}")

    print()
    router.print_distribution()

    # Demonstrate range query
    print("\n=== Range Query Demo ===")
    print("Querying users with ID 0 to 1,500,000:")
    results = router.range_query(0, 1_500_001)
    for user in results:
        print(f"  Found: {user}")


if __name__ == "__main__":
    main()
