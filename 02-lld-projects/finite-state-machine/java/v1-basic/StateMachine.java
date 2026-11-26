import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class StateMachine<C> {
    private final Map<String, State<C>> states;
    private final Map<String, List<Transition<C>>> transitions;
    private final String initialState;
    private final List<StateChangeListener> globalListeners;
    private final boolean globalNotificationsEnabled;
    private State<C> currentState;

    public StateMachine(Map<String, State<C>> states,
                        Map<String, List<Transition<C>>> transitions,
                        String initialState,
                        List<StateChangeListener> globalListeners,
                        boolean globalNotificationsEnabled) {
        this.states = states;
        this.transitions = transitions;
        this.initialState = initialState;
        this.globalListeners = globalListeners;
        this.globalNotificationsEnabled = globalNotificationsEnabled;
        this.currentState = states.get(initialState);
    }

    public void start(C context) {
        if (currentState != null) {
            currentState.onEntry(context);
        }
    }

    public boolean fire(String event, C context) {
        if (currentState == null || currentState.isTerminal()) {
            return false; // Cannot transition from a terminal state or if uninitialized
        }

        List<Transition<C>> availableTransitions = transitions.get(currentState.getName());
        if (availableTransitions == null) {
            return false;
        }

        for (Transition<C> transition : availableTransitions) {
            if (transition.getEvent().equals(event) && transition.evaluateGuard(context)) {
                State<C> nextState = states.get(transition.getToState());
                if (nextState != null) {
                    // Execute exit actions
                    currentState.onExit(context);

                    // Execute transition actions
                    transition.executeActions(context);

                    // Notify listeners
                    if (globalNotificationsEnabled && currentState.isNotificationsEnabled()) {
                        for (StateChangeListener listener : globalListeners) {
                            listener.onTransition(currentState.getName(), nextState.getName(), event);
                        }
                    }

                    // Update state
                    currentState = nextState;

                    // Execute entry actions
                    currentState.onEntry(context);
                    return true;
                }
            }
        }
        return false;
    }

    public String getCurrentState() {
        return currentState != null ? currentState.getName() : null;
    }
    
    public boolean isTerminal() {
        return currentState != null && currentState.isTerminal();
    }
}
