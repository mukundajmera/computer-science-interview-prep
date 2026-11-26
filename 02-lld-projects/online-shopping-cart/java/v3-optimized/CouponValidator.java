package v3_optimized;

import java.util.*;
import v3_optimized.models.*;
import v3_optimized.enums.*;

public class CouponValidator {
    public boolean canApply(List<Coupon> appliedCoupons, Coupon newCoupon) {
        if (!newCoupon.isValid()) return false;
        for (Coupon c : appliedCoupons) {
            if (c.getCode().equals(newCoupon.getCode())) return false;
        }
        if (newCoupon.getType() == DiscountType.PERCENTAGE) {
            long percentCoupons = appliedCoupons.stream()
                .filter(c -> c.getType() == DiscountType.PERCENTAGE)
                .count();
            if (percentCoupons >= 1) return false;
        }
        if (appliedCoupons.size() >= 3) return false;
        return true;
    }
}
