# E-commerce Backend - Problem Statement

## Overview
Design a scalable e-commerce backend similar to Amazon that supports product catalog, shopping cart, order management, inventory control, and payment processing.

---

## Functional Requirements

### Core Features
- **Product Catalog**: Browse, search, and view product details
- **Shopping Cart**: Add/remove items, update quantities, persist across sessions
- **Checkout & Orders**: Place orders, track order status, order history
- **Inventory Management**: Real-time stock tracking, prevent overselling
- **Payment Processing**: Secure payment integration, multiple payment methods
- **User Management**: Registration, authentication, address book

### Secondary Features
- Product reviews and ratings
- Wishlist management
- Order cancellation and returns
- Seller management (multi-vendor)
- Promotions and discounts

---

## Non-Functional Requirements

### Scale
- **Daily Active Users (DAU)**: 50 million
- **Products in Catalog**: 100 million
- **Orders per Day**: 10 million
- **Peak Orders per Second**: 50,000 (flash sales)
- **Cart Operations**: 500 million/day

### Performance
- **Search Latency**: < 200ms P99
- **Add to Cart**: < 100ms P99
- **Checkout**: < 500ms P99
- **Order Confirmation**: < 2 seconds

### Availability
- **Target Availability**: 99.99%
- **Zero Downtime Deployments**: Required
- **Graceful Degradation**: Continue selling during partial outages

### Consistency
- **Inventory**: Strong consistency (no overselling)
- **Orders**: Eventually consistent within 1 second
- **Catalog**: Eventually consistent within 5 seconds

---

## Assumptions

### Traffic Patterns
- Read-heavy: 100:1 read to write ratio
- Flash sale spikes: 100x normal traffic for 1 hour
- Geographic distribution: Global with concentration in US, EU, India
- Mobile vs Web: 70% mobile, 30% web

### Business Assumptions
- Average cart size: 3-5 items
- Cart abandonment: 70%
- Average order value: $50
- Payment success rate: 95%

### Data Size
- Product record: 10 KB average
- Order record: 5 KB average
- User record: 2 KB average

---

## Out of Scope

1. **Fulfillment**: Warehouse management, shipping logistics
2. **Recommendations**: Personalized product suggestions
3. **Customer Support**: Chat, ticketing system
4. **Analytics**: Business intelligence, reporting
5. **Marketing**: Email campaigns, push notifications
6. **Seller Portal**: Seller onboarding, inventory upload
7. **Returns Processing**: Physical return handling
8. **Tax Calculation**: Complex tax rules by jurisdiction
