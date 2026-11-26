"""
Vending Machine System - V3 Optimized

Inventory class managing product slots and coin stock.
"""
from typing import Dict, List, Optional
from coin import Coin
from product import Product
from slot import Slot


class Inventory:
    """Manages the inventory of products and coins in the vending machine."""
    
    def __init__(self):
        self._slots: Dict[str, Slot] = {}
        self._coin_stock: Dict[Coin, int] = {coin: 0 for coin in Coin}
    
    # ============ Slot Operations ============
    
    def add_slot(self, slot: Slot) -> None:
        """Add a slot to the inventory."""
        if slot is None:
            raise ValueError("Slot cannot be null")
        self._slots[slot.code] = slot
    
    def get_slot(self, code: str) -> Optional[Slot]:
        """Get a slot by code."""
        return self._slots.get(code)
    
    def has_slot(self, code: str) -> bool:
        """Check if a slot exists."""
        return code in self._slots
    
    def get_all_slots(self) -> List[Slot]:
        """Get all slots."""
        return list(self._slots.values())
    
    def get_available_products(self) -> List[Product]:
        """Get all products that are in stock."""
        return [slot.product for slot in self._slots.values() if not slot.is_empty]
    
    # ============ Coin Operations ============
    
    def add_coins(self, coin: Coin, count: int) -> None:
        """Add coins to the inventory."""
        if coin is None:
            raise ValueError("Coin cannot be null")
        if count < 0:
            raise ValueError("Count cannot be negative")
        self._coin_stock[coin] = self._coin_stock.get(coin, 0) + count
    
    def add_coins_list(self, coins: List[Coin]) -> None:
        """Add a list of coins to the inventory."""
        for coin in coins:
            self.add_coins(coin, 1)
    
    def get_coin_count(self, coin: Coin) -> int:
        """Get the count of a specific coin type."""
        return self._coin_stock.get(coin, 0)
    
    def get_change(self, amount: float) -> List[Coin]:
        """Calculate and return change using greedy algorithm."""
        change: List[Coin] = []
        amount_in_cents = round(amount * 100)
        
        # Create a copy of coin stock
        available_coins = dict(self._coin_stock)
        
        # Sort coins by value (highest first)
        coins_by_value = sorted(Coin, key=lambda c: c.value, reverse=True)
        
        for coin in coins_by_value:
            coin_value_in_cents = round(coin.value * 100)
            available = available_coins[coin]
            
            while amount_in_cents >= coin_value_in_cents and available > 0:
                change.append(coin)
                amount_in_cents -= coin_value_in_cents
                available -= 1
                available_coins[coin] = available
        
        # If we couldn't make exact change, return empty
        if amount_in_cents > 0:
            return []
        
        # Deduct coins from actual stock
        for coin in change:
            self._coin_stock[coin] -= 1
        
        return change
    
    def can_make_change(self, amount: float) -> bool:
        """Check if exact change can be made for the given amount."""
        amount_in_cents = round(amount * 100)
        available_coins = dict(self._coin_stock)
        
        coins_by_value = sorted(Coin, key=lambda c: c.value, reverse=True)
        
        for coin in coins_by_value:
            coin_value_in_cents = round(coin.value * 100)
            available = available_coins[coin]
            
            while amount_in_cents >= coin_value_in_cents and available > 0:
                amount_in_cents -= coin_value_in_cents
                available -= 1
        
        return amount_in_cents == 0
    
    def get_total_coin_value(self) -> float:
        """Get the total value of all coins in stock."""
        return sum(coin.value * count for coin, count in self._coin_stock.items())
    
    def display_coin_stock(self) -> None:
        """Display the coin stock."""
        print("Coin Stock:")
        for coin in Coin:
            print(f"  {coin.name}: {self._coin_stock[coin]}")
        print(f"  Total Value: ${self.get_total_coin_value():.2f}")
