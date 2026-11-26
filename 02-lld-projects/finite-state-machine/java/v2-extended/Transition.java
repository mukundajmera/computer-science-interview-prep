
import java.util.ArrayList;
import java.util.List;

public class Transition<C, P> {
    private final String fromState;
    private final String toState;
    private final String event;
    private final TransitionGuard<C, P> guard;
    private final List<StateAction<C, P>> transitionActions;

    public Transition(String fromState, String toState, String event, TransitionGuard<C, P> guard) {
        this.fromState = fromState;
        this.toState = toState;
        this.event = event;
        this.guard = guard;
        this.transitionActions = new ArrayList<>();
    }

    public String getFromState() {
        return fromState;
    }

    public String getToState() {
        return toState;
    }

    public String getEvent() {
        return event;
    }

    public void addTransitionAction(StateAction<C, P> action) {
        this.transitionActions.add(action);
    }

    public boolean evaluateGuard(C context, P payload) {
        return guard == null || guard.evaluate(context, payload);
    }

    public void executeActions(C context, P payload) {
        for (StateAction<C, P> action : transitionActions) {
            action.execute(context, payload);
        }
    }
}
