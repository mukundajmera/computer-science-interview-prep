
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class StateMachineBuilder<C, P> {
    private final Map<String, State<C, P>> states = new HashMap<>();
    private final Map<String, List<Transition<C, P>>> transitions = new HashMap<>();
    private String initialState;
    private final List<StateChangeListener> listeners = new ArrayList<>();
    private boolean globalNotificationsEnabled = true;

    public StateMachineBuilder<C, P> withState(String name, boolean isTerminal) {
        states.putIfAbsent(name, new State<>(name, isTerminal));
        return this;
    }

    public StateMachineBuilder<C, P> withInitialState(String name) {
        withState(name, false);
        this.initialState = name;
        return this;
    }

    public StateMachineBuilder<C, P> withEntryAction(String stateName, StateAction<C, P> action) {
        State<C, P> state = states.get(stateName);
        if (state != null) {
            state.addEntryAction(action);
        } else {
            throw new IllegalArgumentException("State " + stateName + " does not exist.");
        }
        return this;
    }

    public StateMachineBuilder<C, P> withExitAction(String stateName, StateAction<C, P> action) {
        State<C, P> state = states.get(stateName);
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

    public StateMachineBuilder<C, P> withGlobalListener(StateChangeListener listener) {
        this.listeners.add(listener);
        return this;
    }

    public StateMachineBuilder<C, P> setNotificationsEnabled(boolean enabled) {
        this.globalNotificationsEnabled = enabled;
        return this;
    }

    public StateMachineBuilder<C, P> setStateNotificationsEnabled(String stateName, boolean enabled) {
        State<C, P> state = states.get(stateName);
        if (state != null) {
            state.setNotificationsEnabled(enabled);
        } else {
            throw new IllegalArgumentException("State " + stateName + " does not exist.");
        }
        return this;
    }

    public StateMachine<C, P> build() {
        if (initialState == null || !states.containsKey(initialState)) {
            throw new IllegalStateException("Initial state must be set and valid.");
        }
        return new StateMachine<>(states, transitions, initialState, listeners, globalNotificationsEnabled);
    }

    public class TransitionBuilder {
        private String fromState;
        private String toState;
        private String event;
        private TransitionGuard<C, P> guard;
        private final List<StateAction<C, P>> actions = new ArrayList<>();

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

        public TransitionBuilder withGuard(TransitionGuard<C, P> guard) {
            this.guard = guard;
            return this;
        }

        public TransitionBuilder withAction(StateAction<C, P> action) {
            this.actions.add(action);
            return this;
        }

        public StateMachineBuilder<C, P> create() {
            if (fromState == null || toState == null || event == null) {
                throw new IllegalStateException("Transition must have fromState, toState, and event.");
            }
            if (!states.containsKey(fromState) || !states.containsKey(toState)) {
                throw new IllegalArgumentException("Both fromState and toState must exist in the StateMachine.");
            }
            Transition<C, P> transition = new Transition<>(fromState, toState, event, guard);
            for (StateAction<C, P> action : actions) {
                transition.addTransitionAction(action);
            }
            transitions.computeIfAbsent(fromState, k -> new ArrayList<>()).add(transition);
            return StateMachineBuilder.this;
        }
    }
}
