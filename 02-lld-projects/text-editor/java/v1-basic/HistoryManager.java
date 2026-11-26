import java.util.Stack;

public class HistoryManager {
    private final Stack<EditorCommand> undoStack;
    private final Stack<EditorCommand> redoStack;

    public HistoryManager() {
        this.undoStack = new Stack<>();
        this.redoStack = new Stack<>();
    }

    public void execute(EditorCommand command) {
        command.execute();
        undoStack.push(command);
        redoStack.clear(); // Clear redo stack on new action
    }

    public void undo() {
        if (!undoStack.isEmpty()) {
            EditorCommand command = undoStack.pop();
            command.undo();
            redoStack.push(command);
        }
    }

    public void redo() {
        if (!redoStack.isEmpty()) {
            EditorCommand command = redoStack.pop();
            command.execute();
            undoStack.push(command);
        }
    }
}
