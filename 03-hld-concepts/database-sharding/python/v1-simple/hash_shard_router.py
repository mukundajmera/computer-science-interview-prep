"""
Simple hash-based database sharding implementation.
Demonstrates the basic concept of distributing data across shards using modulo hashing.
"""

from typing import Dict, Optional, Any


class HashShardRouter:
    """Simple hash-based shard router using modulo hashing."""

    def __init__(self, num_shards: int):
        """Initialize router with specified number of shards.
        
        Args:
            num_shards: Number of shards to distribute data across
        """
        self.num_shards = num_shards
        self.shards: Dict[int, Dict[str, Any]] = {
            i: {} for i in range(num_shards)
        }

    def get_shard_id(self, shard_key: str) -> int:
        """Calculate which shard should store data for given key.
        
        Args:
            shard_key: The key used to determine shard placement
            
        Returns:
            Shard ID (0 to num_shards-1)
        """
        return hash(shard_key) % self.num_shards

    def put(self, shard_key: str, key: str, value: Any) -> None:
        """Store data in the appropriate shard.
        
        Args:
            shard_key: Key used for shard routing
            key: Data key within the shard
            value: Data to store
        """
        shard_id = self.get_shard_id(shard_key)
        self.shards[shard_id][key] = value

    def get(self, shard_key: str, key: str) -> Optional[Any]:
        """Retrieve data from the appropriate shard.
        
        Args:
            shard_key: Key used for shard routing
            key: Data key within the shard
            
        Returns:
            Stored value or None if not found
        """
        shard_id = self.get_shard_id(shard_key)
        return self.shards[shard_id].get(key)

    def delete(self, shard_key: str, key: str) -> bool:
        """Delete data from the appropriate shard.
        
        Args:
            shard_key: Key used for shard routing
            key: Data key within the shard
            
        Returns:
            True if key was deleted, False if not found
        """
        shard_id = self.get_shard_id(shard_key)
        if key in self.shards[shard_id]:
            del self.shards[shard_id][key]
            return True
        return False

    def get_shard_size(self, shard_id: int) -> int:
        """Get the number of items in a specific shard."""
        return len(self.shards[shard_id])

    def get_total_size(self) -> int:
        """Get total number of items across all shards."""
        return sum(len(shard) for shard in self.shards.values())

    def print_distribution(self) -> None:
        """Print distribution statistics."""
        print("=== Shard Distribution ===")
        total = self.get_total_size()
        for i in range(self.num_shards):
            size = len(self.shards[i])
            percentage = (size * 100 // total) if total > 0 else 0
            print(f"Shard {i}: {size} items ({percentage}%)")


def main():
    """Demo for simple hash-based sharding."""
    print("=== Hash-Based Sharding Demo ===\n")

    # Create router with 4 shards
    router = HashShardRouter(4)

    # Simulate storing user data
    print("Storing user data across shards...\n")
    
    users = [
        "user_1001", "user_1002", "user_1003", "user_1004",
        "user_2001", "user_2002", "user_2003", "user_2004",
        "user_3001", "user_3002", "user_3003", "user_3004"
    ]

    for user_id in users:
        user_data = {"name": f"User {user_id}", "email": f"{user_id}@example.com"}
        router.put(user_id, user_id, user_data)
        shard_id = router.get_shard_id(user_id)
        print(f"User {user_id} -> Shard {shard_id}")

    print()
    router.print_distribution()

    # Demonstrate retrieval
    print("\n=== Retrieving Data ===")
    test_user = "user_1001"
    retrieved = router.get(test_user, test_user)
    print(f"Retrieved {test_user}: {retrieved}")

    # Demonstrate consistency
    print("\n=== Consistency Check ===")
    print("Same key always goes to same shard:")
    for i in range(3):
        print(f"user_1001 -> Shard {router.get_shard_id('user_1001')}")


if __name__ == "__main__":
    main()
