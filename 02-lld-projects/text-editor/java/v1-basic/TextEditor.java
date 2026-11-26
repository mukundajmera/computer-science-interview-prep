import java.util.List;

public class TextEditor {
    private final TextBuffer buffer;
    private final Clipboard clipboard;
    private final HistoryManager historyManager;

    public TextEditor() {
        this.buffer = new LineBuffer();
        this.clipboard = new Clipboard();
        this.historyManager = new HistoryManager();
    }

    public void insert(int lineNum, String text) {
        historyManager.execute(new InsertLineCommand(buffer, lineNum, text));
    }

    public void delete(int lineNum) {
        historyManager.execute(new DeleteLineCommand(buffer, lineNum));
    }

    public void deleteRange(int start, int end) {
        historyManager.execute(new DeleteRangeCommand(buffer, start, end));
    }

    public void copy(int start, int end) {
        clipboard.setContent(buffer.getRange(start, end));
    }

    public void paste(int lineNum) {
        List<String> content = clipboard.getContent();
        if (content != null && !content.isEmpty()) {
            historyManager.execute(new PasteCommand(buffer, lineNum, content));
        }
    }

    public void display() {
        List<String> lines = buffer.getAll();
        for (int i = 0; i < lines.size(); i++) {
            System.out.println((i + 1) + ": " + lines.get(i));
        }
    }

    public void displayRange(int start, int end) {
        List<String> lines = buffer.getRange(start, end);
        int currentLine = Math.max(1, start);
        for (String line : lines) {
            System.out.println(currentLine + ": " + line);
            currentLine++;
        }
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
}
