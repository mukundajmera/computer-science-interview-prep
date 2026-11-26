/**
 * Vending Machine System - V1 Basic
 * 
 * Coin enum representing valid currency denominations.
 */

/**
 * Enumeration of coin denominations accepted by the vending machine.
 */
enum Coin {
    PENNY(0.01),
    NICKEL(0.05),
    DIME(0.10),
    QUARTER(0.25),
    HALF_DOLLAR(0.50),
    DOLLAR(1.00);

    private final double value;

    Coin(double value) {
        this.value = value;
    }

    public double getValue() {
        return value;
    }

    @Override
    public String toString() {
        return name() + " ($" + String.format("%.2f", value) + ")";
    }
}
