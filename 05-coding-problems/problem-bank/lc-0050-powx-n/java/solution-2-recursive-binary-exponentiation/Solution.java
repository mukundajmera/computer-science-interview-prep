class Solution {
    public double myPow(double x, int n) {
        long exponent = n;
        if (exponent < 0) {
            return 1.0 / fastPow(x, -exponent);
        }
        return fastPow(x, exponent);
    }

    private double fastPow(double base, long exponent) {
        if (exponent == 0) {
            return 1.0;
        }
        double half = fastPow(base, exponent / 2);
        double squared = half * half;
        if ((exponent & 1L) == 1L) {
            return squared * base;
        }
        return squared;
    }
}
