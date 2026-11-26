package v3_optimized.models;

import java.util.*;
import v3_optimized.enums.*;

public class Coupon {
    private final String code;
    private final DiscountType type;
    private final double value;
    private final double minAmount;
    private final double maxDiscount;
    private final Date expiresAt;
    private final int usageLimit;
    private int usedCount;
    
    public Coupon(String code, DiscountType type, double value, double minAmount, 
                  double maxDiscount, Date expiresAt, int usageLimit) {
        this.code = code; this.type = type; this.value = value; this.minAmount = minAmount;
        this.maxDiscount = maxDiscount; this.expiresAt = expiresAt; this.usageLimit = usageLimit;
    }
    
    public String getCode() { return code; }
    public DiscountType getType() { return type; }
    public boolean isValid() { return !isExpired() && usedCount < usageLimit; }
    public boolean isExpired() { return new Date().after(expiresAt); }
    public boolean isApplicable(double subtotal) { return isValid() && subtotal >= minAmount; }
    
    public double calculateDiscount(double subtotal) {
        if (!isApplicable(subtotal)) return 0;
        double discount = type == DiscountType.PERCENTAGE ? subtotal * (value / 100) : value;
        return Math.min(discount, maxDiscount);
    }
    
    public synchronized void use() { usedCount++; }
}
