# Code Walkthrough: Online Shopping Cart

## Overview

E-commerce cart with inventory management and checkout.

---

## Core Flow

```
Browse → Add to Cart → Update Qty → Checkout → Payment → Order
```

---

## Key Classes

```java
class ShoppingCart {
    Map<Product, Integer> items;  // product -> quantity
    
    void addItem(Product p, int qty);
    void removeItem(Product p);
    void updateQuantity(Product p, int qty);
    double getTotal();
    Order checkout(PaymentMethod payment);
}

class InventoryService {
    boolean checkStock(Product p, int qty);
    void reserveStock(Product p, int qty);
    void releaseStock(Product p, int qty);
}
```

---

## Interview Questions

### 1. "How to handle cart abandonment?"

- Persist cart to DB/Redis
- Background job to release reserved stock after timeout
- Send reminder emails

### 2. "How to apply discount codes?"

```java
interface DiscountStrategy {
    double apply(double total, String code);
}

class PercentageDiscount implements DiscountStrategy { ... }
class FlatDiscount implements DiscountStrategy { ... }
class BuyOneGetOne implements DiscountStrategy { ... }
```

### 3. "How to handle inventory race conditions?"

```java
// Optimistic locking
@Version
private long version;

// Or pessimistic
synchronized void purchaseItem(Product p, int qty) {
    if (inventory.get(p) >= qty) {
        inventory.put(p, inventory.get(p) - qty);
    }
}
```

### 4. "How to implement wishlist?"

```java
class Wishlist {
    User user;
    List<Product> products;
    
    void moveToCart(Product p) {
        cart.addItem(p, 1);
        products.remove(p);
    }
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Strategy** | Discount/pricing |
| **Observer** | Stock alerts |
| **Factory** | Create orders |
| **Singleton** | Cart service |
