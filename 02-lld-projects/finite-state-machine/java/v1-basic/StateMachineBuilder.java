import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class StateMachineBuilder<C> {
    private final Map<String, State<C>> states = new HashMap<>();
    private final Map<String, List<Transition<C>>> transitions = new HashMap<>();
    private String initialState;
    private final List<StateChangeListener> listeners = new ArrayList<>();
    private boolean globalNotificationsEnabled = true;

    public StateMachineBuilder<C> withState(String name, boolean isTerminal) {
        states.putIfAbsent(name, new State<>(name, isTerminal));
        return this;
    }

    public StateMachineBuilder<C> withInitialState(String name) {
        withState(name, false);
        this.initialState = name;
        return this;
    }

    public StateMachineBuilder<C> withEntryAction(String stateName, StateAction<C> action) {
        State<C> state = states.get(stateName);
        if (state != null) {
            state.addEntryAction(action);
        } else {
            throw new IllegalArgumentException("State " + stateName + " does not exist.");
        }
        return this;
    }

    public StateMachineBuilder<C> withExitAction(String stateName, StateAction<C> action) {
        State<C> state = states.get(stateName);
        if (state != null) {
            state.addExitAction(action);
        } else {
            throw new IllegalArgumentException("State " + stateName + " does not exist.");
        }
        return this;
    }

    public TransitionBuilder withTransition() {
        return new TransitionBuilder();
    }

    public StateMachineBuilder<C> withGlobalListener(StateChangeListener listener) {
        this.listeners.add(listener);
        return this;
    }

    public StateMachineBuilder<C> setNotificationsEnabled(boolean enabled) {
        this.globalNotificationsEnabled = enabled;
        return this;
    }

    public StateMachineBuilder<C> setStateNotificationsEnabled(String stateName, boolean enabled) {
        State<C> state = states.get(stateName);
        if (state != null) {
            state.setNotificationsEnabled(enabled);
        } else {
            throw new IllegalArgumentException("State " + stateName + " does not exist.");
        }
        return this;
    }

    public StateMachine<C> build() {
        if (initialState == null || !states.containsKey(initialState)) {
            throw new IllegalStateException("Initial state must be set and valid.");
        }
        return new StateMachine<>(states, transitions, initialState, listeners, globalNotificationsEnabled);
    }

    public class TransitionBuilder {
        private String fromState;
        private String toState;
        private String event;
        private TransitionGuard<C> guard;
        private final List<StateAction<C>> actions = new ArrayList<>();

        public TransitionBuilder from(String state) {
            this.fromState = state;
            return this;
        }

        public TransitionBuilder to(String state) {
            this.toState = state;
            return this;
        }

        public TransitionBuilder on(String event) {
            this.event = event;
            return this;
        }

        public TransitionBuilder withGuard(TransitionGuard<C> guard) {
            this.guard = guard;
            return this;
        }

        public TransitionBuilder withAction(StateAction<C> action) {
            this.actions.add(action);
            return this;
        }

        public StateMachineBuilder<C> create() {
            if (fromState == null || toState == null || event == null) {
                throw new IllegalStateException("Transition must have fromState, toState, and event.");
            }
            if (!states.containsKey(fromState) || !states.containsKey(toState)) {
                throw new IllegalArgumentException("Both fromState and toState must exist in the StateMachine.");
            }
            Transition<C> transition = new Transition<>(fromState, toState, event, guard);
            for (StateAction<C> action : actions) {
                transition.addTransitionAction(action);
            }
            transitions.computeIfAbsent(fromState, k -> new ArrayList<>()).add(transition);
            return StateMachineBuilder.this;
        }
    }
}
