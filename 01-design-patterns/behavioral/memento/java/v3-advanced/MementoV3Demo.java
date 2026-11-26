/**
 * Memento Pattern - V3 Advanced: Transactional checkpoints for a text editor.
 */

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Stack;

final class TransactionMemento {
    private final String content;
    private final int cursorPosition;
    private final String label;
    private final Instant createdAt;

    TransactionMemento(String content, int cursorPosition, String label) {
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

class TransactionalTextEditor {
    private String content = "";
    private int cursorPosition = 0;

    /**
     * Inserts text at the cursor.
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

    TransactionMemento save(String label) {
        return new TransactionMemento(content, cursorPosition, label);
    }

    void restore(TransactionMemento memento) {
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

class CheckpointHistory {
    private final TransactionalTextEditor editor;
    private final Stack<TransactionMemento> undoStack = new Stack<>();
    private final Stack<TransactionMemento> redoStack = new Stack<>();
    private final Map<String, TransactionMemento> checkpoints = new HashMap<>();
    private TransactionMemento activeTransaction;

    CheckpointHistory(TransactionalTextEditor editor) {
        this.editor = editor;
    }

    void snapshot(String label) {
        undoStack.push(editor.save(label));
        redoStack.clear();
    }

    void saveCheckpoint(String name) {
        checkpoints.put(name, editor.save(name));
    }

    void restoreCheckpoint(String name) {
        TransactionMemento checkpoint = checkpoints.get(name);
        if (checkpoint == null) {
            throw new IllegalArgumentException("Unknown checkpoint: " + name);
        }
        activeTransaction = null;
        editor.restore(checkpoint);
    }

    void beginTransaction(String label) {
        if (activeTransaction != null) {
            throw new IllegalStateException("transaction already active");
        }
        activeTransaction = editor.save(label);
    }

    void rollbackTransaction() {
        if (activeTransaction == null) {
            throw new IllegalStateException("no active transaction");
        }
        editor.restore(activeTransaction);
        activeTransaction = null;
    }

    void commitTransaction(String label) {
        if (activeTransaction == null) {
            throw new IllegalStateException("no active transaction");
        }
        activeTransaction = null;
        snapshot(label);
    }

    TransactionMemento undo() {
        if (undoStack.size() > 1) {
            redoStack.push(undoStack.pop());
            TransactionMemento memento = undoStack.peek();
            editor.restore(memento);
            return memento;
        }
        if (!undoStack.isEmpty()) {
            editor.restore(undoStack.peek());
            return undoStack.peek();
        }
        return null;
    }

    TransactionMemento redo() {
        if (redoStack.isEmpty()) {
            return null;
        }
        TransactionMemento memento = redoStack.pop();
        undoStack.push(memento);
        editor.restore(memento);
        return memento;
    }
}

public class MementoV3Demo {
    public static void main(String[] args) {
        TransactionalTextEditor editor = new TransactionalTextEditor();
        CheckpointHistory history = new CheckpointHistory(editor);

        history.snapshot("empty");
        editor.type("Draft");
        history.snapshot("draft");
        history.saveCheckpoint("approved-draft");

        history.beginTransaction("risky rewrite");
        editor.type(" unsafe");
        history.rollbackTransaction();
        System.out.println("Rollback: " + editor);

        history.beginTransaction("publish edit");
        editor.type(" v2");
        history.commitTransaction("published");
        System.out.println("Commit: " + editor);
    }
}
