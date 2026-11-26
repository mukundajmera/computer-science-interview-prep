
import java.util.ArrayList;
import java.util.List;

public class State<C, P> {
    private final String name;
    private final boolean isTerminal;
    private final List<StateAction<C, P>> entryActions;
    private final List<StateAction<C, P>> exitActions;
    private boolean notificationsEnabled;

    public State(String name, boolean isTerminal) {
        this.name = name;
        this.isTerminal = isTerminal;
        this.entryActions = new ArrayList<>();
        this.exitActions = new ArrayList<>();
        this.notificationsEnabled = true;
    }

    public void addEntryAction(StateAction<C, P> action) {
        this.entryActions.add(action);
    }

    public void addExitAction(StateAction<C, P> action) {
        this.exitActions.add(action);
    }

    public String getName() {
        return name;
    }

    public boolean isTerminal() {
        return isTerminal;
    }

    public boolean isNotificationsEnabled() {
        return notificationsEnabled;
    }

    public void setNotificationsEnabled(boolean notificationsEnabled) {
        this.notificationsEnabled = notificationsEnabled;
    }

    public void onEntry(C context, P payload) {
        for (StateAction<C, P> action : entryActions) {
            action.execute(context, payload);
        }
    }

    public void onExit(C context, P payload) {
        for (StateAction<C, P> action : exitActions) {
            action.execute(context, payload);
        }
    }
}
