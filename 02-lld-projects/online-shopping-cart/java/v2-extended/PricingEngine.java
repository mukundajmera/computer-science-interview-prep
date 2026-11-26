package v2_extended;

import java.util.*;
import java.util.concurrent.*;
import v2_extended.models.*;
import v2_extended.enums.*;
public class PricingEngine {
    private double taxRate = 0.08; // 8%
    private double shippingPerKg = 5.0;
    private double freeShippingThreshold = 100.0;
    
    public PriceSummary calculate(Cart cart, Coupon coupon) {
        PriceSummary summary = new PriceSummary();
        summary.subtotal = cart.getSubtotal();
        
        if (coupon != null && coupon.isApplicable(summary.subtotal)) {
            summary.discount = coupon.calculateDiscount(summary.subtotal);
            summary.couponCode = coupon.getCode();
        }
        
        double afterDiscount = summary.subtotal - summary.discount;
        summary.tax = afterDiscount * taxRate;
        summary.shipping = afterDiscount >= freeShippingThreshold ? 0 : cart.getTotalWeight() * shippingPerKg;
        summary.total = afterDiscount + summary.tax + summary.shipping;
        
        return summary;
    }
}