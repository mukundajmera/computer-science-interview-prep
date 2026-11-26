"""
Online Shopping Cart - V1 Basic Demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shopping_entities import (
    Category, Product, ShoppingService
)


def main():
    """Demonstrate basic shopping cart functionality."""
    
    print("=" * 60)
    print("Online Shopping Cart - V1 Basic Demo")
    print("=" * 60)
    
    # Reset for clean demo
    ShoppingService.reset_instance()
    service = ShoppingService()
    
    # Create categories
    electronics = Category("CAT1", "Electronics")
    books = Category("CAT2", "Books")
    
    service.add_category(electronics)
    service.add_category(books)
    
    # Create products
    laptop = Product("P1", "MacBook Pro", "Apple laptop with M2 chip", 1999.99, electronics, 2.0)
    phone = Product("P2", "iPhone 15", "Latest iPhone", 999.99, electronics, 0.2)
    headphones = Product("P3", "AirPods Pro", "Wireless earbuds", 249.99, electronics, 0.1)
    python_book = Product("P4", "Python Programming", "Learn Python", 49.99, books, 0.5)
    
    # Add products with stock
    service.add_product(laptop, 10)
    service.add_product(phone, 50)
    service.add_product(headphones, 100)
    service.add_product(python_book, 25)
    
    print("\n1. Products available:")
    for product in [laptop, phone, headphones, python_book]:
        stock = service.inventory.get_stock(product.id)
        print(f"   - {product} (Stock: {stock})")
    
    # Create cart for user
    cart = service.create_cart("user123")
    print(f"\n2. Created cart: {cart.id}")
    
    # Add items to cart
    print("\n3. Adding items to cart...")
    service.add_to_cart(cart.id, "P1", 1)  # 1 laptop
    service.add_to_cart(cart.id, "P2", 2)  # 2 phones
    service.add_to_cart(cart.id, "P3", 1)  # 1 headphones
    
    cart.display()
    
    # Update quantity
    print("\n4. Updating phone quantity to 3...")
    service.update_cart_quantity(cart.id, "P2", 3)
    cart.display()
    
    # Remove item
    print("\n5. Removing headphones...")
    service.remove_from_cart(cart.id, "P3")
    cart.display()
    
    # Search products
    print("\n6. Search for 'Pro':")
    results = service.search_products("Pro")
    for p in results:
        print(f"   - {p}")
    
    # Get products by category
    print("\n7. Electronics products:")
    electronics_products = service.get_products_by_category("CAT1")
    for p in electronics_products:
        print(f"   - {p}")
    
    # Checkout
    print("\n8. Checkout...")
    success = service.checkout(cart.id)
    
    if success:
        print("\n9. Stock after checkout:")
        print(f"   - MacBook Pro: {service.inventory.get_stock('P1')}")
        print(f"   - iPhone 15: {service.inventory.get_stock('P2')}")
    
    # Cart should be empty now
    cart.display()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
