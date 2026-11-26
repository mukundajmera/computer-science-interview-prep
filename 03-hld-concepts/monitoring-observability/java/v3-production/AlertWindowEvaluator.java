public class AlertWindowEvaluator {
    public boolean shouldFire(double value, double threshold) {
        return value > threshold;
    }
}
