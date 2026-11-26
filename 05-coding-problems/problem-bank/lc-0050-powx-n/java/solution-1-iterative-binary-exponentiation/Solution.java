class Solution {
    public double myPow(double x, int n) {
        long exponent = n;
        double base = x;
        if (exponent < 0) {
            base = 1.0 / base;
            exponent = -exponent;
        }

        double result = 1.0;
        while (exponent > 0) {
            if ((exponent & 1L) == 1L) {
                result *= base;
            }
            base *= base;
            exponent >>= 1;
        }
        return result;
    }
}
