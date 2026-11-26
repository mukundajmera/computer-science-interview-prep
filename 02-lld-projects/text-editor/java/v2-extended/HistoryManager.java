

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

public class HistoryManager {
    private final int limit;
    private final LinkedList<Command> undoStack;
    private final LinkedList<Command> redoStack;
    private boolean isRecording;
    private List<Command> currentMacro;

    public HistoryManager(int limit) {
        this.limit = limit;
        this.undoStack = new LinkedList<>();
        this.redoStack = new LinkedList<>();
        this.isRecording = false;
        this.currentMacro = new ArrayList<>();
    }

    public void execute(Command command) {
        command.execute();
        if (isRecording) {
            currentMacro.add(command);
        } else {
            undoStack.push(command);
            if (undoStack.size() > limit) {
                undoStack.removeLast();
            }
            redoStack.clear();
        }
    }

    public void undo() {
        if (isRecording) {
            return; // Don't undo while recording
        }
        if (!undoStack.isEmpty()) {
            Command command = undoStack.pop();
            command.undo();
            redoStack.push(command);
        }
    }

    public void redo() {
        if (isRecording) {
            return;
        }
        if (!redoStack.isEmpty()) {
            Command command = redoStack.pop();
            command.execute();
            undoStack.push(command);
        }
    }

    public void startRecording() {
        isRecording = true;
        currentMacro = new ArrayList<>();
    }

    public MacroCommand stopRecording() {
        isRecording = false;
        if (currentMacro.isEmpty()) {
            return null;
        }
        MacroCommand macro = new MacroCommand(currentMacro);
        undoStack.push(macro);
        if (undoStack.size() > limit) {
            undoStack.removeLast();
        }
        redoStack.clear();
        return macro;
    }
}
