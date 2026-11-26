
public interface StateChangeListener {
    void onTransition(String fromState, String toState, String event);
}
