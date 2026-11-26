package v2_extended.models;

import java.util.*;
import java.util.concurrent.*;
import v2_extended.*;
public class PriceSummary {
    public double subtotal, discount, tax, shipping, total;
    public String couponCode;
    
    public void display() {
        System.out.printf("Subtotal: $%.2f%n", subtotal);
        if (discount > 0) System.out.printf("Discount (%s): -$%.2f%n", couponCode, discount);
        System.out.printf("Tax: $%.2f%n", tax);
        System.out.printf("Shipping: $%.2f%n", shipping);
        System.out.printf("Total: $%.2f%n", total);
    }
}