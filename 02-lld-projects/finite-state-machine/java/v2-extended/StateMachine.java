
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class StateMachine<C, P> {
    private final Map<String, State<C, P>> states;
    private final Map<String, List<Transition<C, P>>> transitions;
    private final String initialState;
    private final List<StateChangeListener> globalListeners;
    private final boolean globalNotificationsEnabled;
    private State<C, P> currentState;

    public StateMachine(Map<String, State<C, P>> states,
                        Map<String, List<Transition<C, P>>> transitions,
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

    public void start(C context, P payload) {
        if (currentState != null) {
            currentState.onEntry(context, payload);
        }
    }

    public boolean fire(String event, C context, P payload) {
        if (currentState == null || currentState.isTerminal()) {
            return false; // Cannot transition from a terminal state or if uninitialized
        }

        List<Transition<C, P>> availableTransitions = transitions.get(currentState.getName());
        if (availableTransitions == null) {
            return false;
        }

        for (Transition<C, P> transition : availableTransitions) {
            if (transition.getEvent().equals(event) && transition.evaluateGuard(context, payload)) {
                State<C, P> nextState = states.get(transition.getToState());
                if (nextState != null) {
                    // Execute exit actions
                    currentState.onExit(context, payload);

                    // Execute transition actions
                    transition.executeActions(context, payload);

                    // Notify listeners
                    if (globalNotificationsEnabled && currentState.isNotificationsEnabled()) {
                        for (StateChangeListener listener : globalListeners) {
                            listener.onTransition(currentState.getName(), nextState.getName(), event);
                        }
                    }

                    // Update state
                    currentState = nextState;

                    // Execute entry actions
                    currentState.onEntry(context, payload);
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
