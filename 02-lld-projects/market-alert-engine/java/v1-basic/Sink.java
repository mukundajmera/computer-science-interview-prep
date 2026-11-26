public interface Sink {
    void send(AlertRule rule, Tick tick);
}
