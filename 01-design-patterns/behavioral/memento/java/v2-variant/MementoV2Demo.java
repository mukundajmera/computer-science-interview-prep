/**
 * Memento Pattern - V2 Variant: Bounded labeled text editor history.
 */

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

final class VersionedEditorMemento {
    private final String content;
    private final int cursorPosition;
    private final String label;
    private final Instant createdAt;

    VersionedEditorMemento(String content, int cursorPosition, String label) {
        this.content = content;
        this.cursorPosition = cursorPosition;
        this.label = label;
        this.createdAt = Instant.now();
    }

    String getContent() {
        return content;
    }

    int getCursorPosition() {
        return cursorPosition;
    }

    String getLabel() {
        return label;
    }

    Instant getCreatedAt() {
        return createdAt;
    }
}

class VersionedTextEditor {
    private String content = "";
    private int cursorPosition = 0;

    /**
     * Inserts text at the current cursor position.
     *
     * Time Complexity: O(n)
     * Space Complexity: O(n)
     */
    void type(String text) {
        content = content.substring(0, cursorPosition) + text + content.substring(cursorPosition);
        cursorPosition += text.length();
    }

    /**
     * Deletes one character before the cursor.
     *
     * Time Complexity: O(n)
     * Space Complexity: O(n)
     */
    void delete() {
        if (cursorPosition > 0) {
            content = content.substring(0, cursorPosition - 1) + content.substring(cursorPosition);
            cursorPosition--;
        }
    }

    void moveCursor(int position) {
        cursorPosition = Math.max(0, Math.min(position, content.length()));
    }

    VersionedEditorMemento save(String label) {
        return new VersionedEditorMemento(content, cursorPosition, label);
    }

    void restore(VersionedEditorMemento memento) {
        content = memento.getContent();
        cursorPosition = memento.getCursorPosition();
    }

    String getContent() {
        return content;
    }

    @Override
    public String toString() {
        return "Content: \"" + content + "\" (cursor at " + cursorPosition + ")";
    }
}

class BoundedEditorHistory {
    private final int maxSnapshots;
    private final LinkedList<VersionedEditorMemento> undoStack = new LinkedList<>();
    private final LinkedList<VersionedEditorMemento> redoStack = new LinkedList<>();

    BoundedEditorHistory(int maxSnapshots) {
        if (maxSnapshots < 1) {
            throw new IllegalArgumentException("maxSnapshots must be positive");
        }
        this.maxSnapshots = maxSnapshots;
    }

    void push(VersionedEditorMemento memento) {
        undoStack.addLast(memento);
        if (undoStack.size() > maxSnapshots) {
            undoStack.removeFirst();
        }
        redoStack.clear();
    }

    VersionedEditorMemento undo() {
        if (undoStack.size() > 1) {
            redoStack.addLast(undoStack.removeLast());
            return undoStack.getLast();
        }
        return undoStack.isEmpty() ? null : undoStack.getLast();
    }

    VersionedEditorMemento redo() {
        if (redoStack.isEmpty()) {
            return null;
        }
        VersionedEditorMemento memento = redoStack.removeLast();
        undoStack.addLast(memento);
        return memento;
    }

    List<String> labels() {
        List<String> labels = new ArrayList<>();
        for (VersionedEditorMemento memento : undoStack) {
            labels.add(memento.getLabel());
        }
        return labels;
    }
}

public class MementoV2Demo {
    public static void main(String[] args) {
        VersionedTextEditor editor = new VersionedTextEditor();
        BoundedEditorHistory history = new BoundedEditorHistory(3);

        history.push(editor.save("empty"));
        editor.type("Hello");
        history.push(editor.save("greeting"));
        editor.type(" World");
        history.push(editor.save("subject"));
        editor.delete();
        history.push(editor.save("trimmed"));

        System.out.println("History: " + history.labels());
        editor.restore(history.undo());
        System.out.println("Undo: " + editor);
    }
}
