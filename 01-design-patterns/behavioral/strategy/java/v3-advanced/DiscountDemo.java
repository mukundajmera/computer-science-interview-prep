/**
 * Strategy Pattern - V3 Advanced: Composable Discount Strategies
 */

import java.util.*;
import java.util.function.Function;

// Strategy Interface
interface DiscountStrategy {
    double apply(double price);
    String getDescription();
}

// Concrete Strategies
class NoDiscount implements DiscountStrategy {
    @Override
    public double apply(double price) { return price; }
    
    @Override
    public String getDescription() { return "No discount"; }
}

class PercentageDiscount implements DiscountStrategy {
    private final double percentage;
    
    public PercentageDiscount(double percentage) {
        this.percentage = percentage;
    }
    
    @Override
    public double apply(double price) {
        return price * (1 - percentage / 100);
    }
    
    @Override
    public String getDescription() {
        return String.format("%.0f%% off", percentage);
    }
}

class FixedDiscount implements DiscountStrategy {
    private final double amount;
    
    public FixedDiscount(double amount) {
        this.amount = amount;
    }
    
    @Override
    public double apply(double price) {
        return Math.max(0, price - amount);
    }
    
    @Override
    public String getDescription() {
        return String.format("$%.2f off", amount);
    }
}

class ThresholdDiscount implements DiscountStrategy {
    private final double threshold;
    private final DiscountStrategy discount;
    
    public ThresholdDiscount(double threshold, DiscountStrategy discount) {
        this.threshold = threshold;
        this.discount = discount;
    }
    
    @Override
    public double apply(double price) {
        return price >= threshold ? discount.apply(price) : price;
    }
    
    @Override
    public String getDescription() {
        return String.format("%s (orders over $%.0f)", discount.getDescription(), threshold);
    }
}

// Composite Strategy - Chain multiple discounts
class CompositeDiscount implements DiscountStrategy {
    private final List<DiscountStrategy> strategies = new ArrayList<>();
    
    public CompositeDiscount add(DiscountStrategy strategy) {
        strategies.add(strategy);
        return this;
    }
    
    @Override
    public double apply(double price) {
        double result = price;
        for (DiscountStrategy strategy : strategies) {
            result = strategy.apply(result);
        }
        return result;
    }
    
    @Override
    public String getDescription() {
        StringBuilder sb = new StringBuilder("Combined: ");
        for (int i = 0; i < strategies.size(); i++) {
            if (i > 0) sb.append(" + ");
            sb.append(strategies.get(i).getDescription());
        }
        return sb.toString();
    }
}

// Best Discount Selector
class BestDiscountSelector implements DiscountStrategy {
    private final List<DiscountStrategy> strategies = new ArrayList<>();
    
    public BestDiscountSelector add(DiscountStrategy strategy) {
        strategies.add(strategy);
        return this;
    }
    
    @Override
    public double apply(double price) {
        return strategies.stream()
            .mapToDouble(s -> s.apply(price))
            .min()
            .orElse(price);
    }
    
    @Override
    public String getDescription() {
        return "Best available discount";
    }
}

// Context with strategy selection
class PricingEngine {
    private DiscountStrategy discountStrategy = new NoDiscount();
    
    public void setDiscountStrategy(DiscountStrategy strategy) {
        this.discountStrategy = strategy;
        System.out.println("Applied: " + strategy.getDescription());
    }
    
    public double calculatePrice(double basePrice) {
        double finalPrice = discountStrategy.apply(basePrice);
        System.out.printf("Base: $%.2f -> Final: $%.2f%n", basePrice, finalPrice);
        return finalPrice;
    }
}

public class DiscountDemo {
    public static void main(String[] args) {
        PricingEngine engine = new PricingEngine();
        double basePrice = 100.00;
        
        System.out.println("=== Simple Discounts ===");
        engine.setDiscountStrategy(new PercentageDiscount(20));
        engine.calculatePrice(basePrice);
        
        engine.setDiscountStrategy(new FixedDiscount(15));
        engine.calculatePrice(basePrice);
        
        System.out.println("\n=== Threshold Discount ===");
        engine.setDiscountStrategy(new ThresholdDiscount(50, new PercentageDiscount(10)));
        engine.calculatePrice(40);   // Below threshold
        engine.calculatePrice(100);  // Above threshold
        
        System.out.println("\n=== Composite Discount ===");
        CompositeDiscount combo = new CompositeDiscount()
            .add(new PercentageDiscount(10))    // 10% off first
            .add(new FixedDiscount(5));          // Then $5 off
        engine.setDiscountStrategy(combo);
        engine.calculatePrice(100);  // 100 -> 90 -> 85
        
        System.out.println("\n=== Best Discount Selector ===");
        BestDiscountSelector best = new BestDiscountSelector()
            .add(new PercentageDiscount(15))  // $85
            .add(new FixedDiscount(20));      // $80 <- Best
        engine.setDiscountStrategy(best);
        engine.calculatePrice(100);
        
        // Lambda-based strategy (Java 8+)
        System.out.println("\n=== Lambda Strategy ===");
        DiscountStrategy vipDiscount = new DiscountStrategy() {
            @Override
            public double apply(double price) { return price * 0.7; }
            
            @Override
            public String getDescription() { return "VIP 30% off"; }
        };
        engine.setDiscountStrategy(vipDiscount);
        engine.calculatePrice(100);
    }
}
