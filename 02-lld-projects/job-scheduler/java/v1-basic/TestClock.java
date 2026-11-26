package v1_basic;

public class TestClock implements Clock {
    private long currentTime;

    public TestClock() {
        this.currentTime = 0;
    }

    public TestClock(long startTime) {
        this.currentTime = startTime;
    }

    @Override
    public long now() {
        return currentTime;
    }

    public void advance(long millis) {
        this.currentTime += millis;
    }

    public void setTime(long millis) {
        this.currentTime = millis;
    }
}
