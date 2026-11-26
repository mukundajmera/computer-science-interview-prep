import java.util.ArrayList;
import java.util.List;

public class State<C> {
    private final String name;
    private final boolean isTerminal;
    private final List<StateAction<C>> entryActions;
    private final List<StateAction<C>> exitActions;
    private boolean notificationsEnabled;

    public State(String name, boolean isTerminal) {
        this.name = name;
        this.isTerminal = isTerminal;
        this.entryActions = new ArrayList<>();
        this.exitActions = new ArrayList<>();
        this.notificationsEnabled = true;
    }

    public void addEntryAction(StateAction<C> action) {
        this.entryActions.add(action);
    }

    public void addExitAction(StateAction<C> action) {
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

    public void onEntry(C context) {
        for (StateAction<C> action : entryActions) {
            action.execute(context);
        }
    }

    public void onExit(C context) {
        for (StateAction<C> action : exitActions) {
            action.execute(context);
        }
    }
}
