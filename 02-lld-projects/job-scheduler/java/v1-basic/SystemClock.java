package v1_basic;

public class SystemClock implements Clock {
    @Override
    public long now() {
        return System.currentTimeMillis();
    }
}
