

import java.util.List;

public class TextEditor {
    private final MementoBuffer buffer;
    private final HistoryManager historyManager;

    public TextEditor(int historyLimit) {
        this.buffer = new MementoBuffer();
        this.historyManager = new HistoryManager(historyLimit);
    }

    public void insert(int lineNum, String text) {
        historyManager.execute(new InsertCommand(buffer, lineNum, text));
    }

    public void delete(int lineNum) {
        historyManager.execute(new DeleteCommand(buffer, lineNum));
    }

    public void replace(int lineNum, String text) {
        historyManager.execute(new ReplaceCommand(buffer, lineNum, text));
    }

    public List<String> getAllLines() {
        return buffer.getAll();
    }

    public void undo() {
        historyManager.undo();
    }

    public void redo() {
        historyManager.redo();
    }

    public void startMacro() {
        historyManager.startRecording();
    }

    public MacroCommand stopMacro() {
        return historyManager.stopRecording();
    }

    public void executeMacro(MacroCommand macro) {
        if (macro != null) {
            historyManager.execute(macro);
        }
    }
}
