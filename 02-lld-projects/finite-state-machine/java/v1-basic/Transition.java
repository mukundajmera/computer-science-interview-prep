import java.util.ArrayList;
import java.util.List;

public class Transition<C> {
    private final String fromState;
    private final String toState;
    private final String event;
    private final TransitionGuard<C> guard;
    private final List<StateAction<C>> transitionActions;

    public Transition(String fromState, String toState, String event, TransitionGuard<C> guard) {
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

    public void addTransitionAction(StateAction<C> action) {
        this.transitionActions.add(action);
    }

    public boolean evaluateGuard(C context) {
        return guard == null || guard.evaluate(context);
    }

    public void executeActions(C context) {
        for (StateAction<C> action : transitionActions) {
            action.execute(context);
        }
    }
}
