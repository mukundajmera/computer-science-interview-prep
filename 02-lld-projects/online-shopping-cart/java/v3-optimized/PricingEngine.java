package v3_optimized;

import java.util.*;
import v3_optimized.models.*;

public class PricingEngine {
    private double taxRate = 0.08; 
    private double shippingPerKg = 5.0;
    private double freeShippingThreshold = 100.0;
    
    public PriceSummary calculate(Cart cart, Coupon coupon) {
        List<Coupon> singleList = coupon != null ? Collections.singletonList(coupon) : Collections.emptyList();
        return calculate(cart, singleList);
    }

    public PriceSummary calculate(Cart cart, List<Coupon> coupons) {
        PriceSummary summary = new PriceSummary();
        summary.subtotal = cart.getSubtotal();
        summary.discount = 0;
        
        double currentSubtotal = summary.subtotal;
        StringBuilder codes = new StringBuilder();
        
        for (Coupon coupon : coupons) {
            if (coupon.isApplicable(currentSubtotal)) {
                double discount = coupon.calculateDiscount(currentSubtotal);
                summary.discount += discount;
                currentSubtotal = Math.max(0, currentSubtotal - discount);
                codes.append(coupon.getCode()).append(" ");
            }
        }
        
        summary.couponCode = codes.toString().trim();
        if (summary.discount > summary.subtotal) {
            summary.discount = summary.subtotal; 
        }
        
        double afterDiscount = summary.subtotal - summary.discount;
        summary.tax = afterDiscount * taxRate;
        summary.shipping = afterDiscount >= freeShippingThreshold ? 0 : cart.getTotalWeight() * shippingPerKg;
        summary.total = afterDiscount + summary.tax + summary.shipping;
        
        return summary;
    }
}
