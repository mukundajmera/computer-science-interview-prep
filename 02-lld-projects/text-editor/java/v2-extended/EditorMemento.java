

import java.util.ArrayList;
import java.util.List;

public class EditorMemento {
    private final List<String> state;

    public EditorMemento(List<String> state) {
        this.state = new ArrayList<>(state);
    }

    public List<String> getState() {
        return state;
    }
}
