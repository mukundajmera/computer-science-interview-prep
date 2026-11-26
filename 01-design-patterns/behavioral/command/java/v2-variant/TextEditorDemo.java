/**
 * Command Pattern - V2 Variant: Text Editor with Undo/Redo
 */

import java.util.*;

interface EditorCommand {
    void execute();
    void undo();
}

class TextEditor {
    private final StringBuilder content = new StringBuilder();

    public String getContent() {
        return content.toString();
    }

    public void insert(int index, String text) {
        if (index < 0 || index > content.length()) {
            throw new IllegalArgumentException("index out of bounds");
        }
        content.insert(index, text);
    }

    public String delete(int index, int length) {
        if (index < 0 || length < 0 || index + length > content.length()) {
            throw new IllegalArgumentException("delete range out of bounds");
        }
        String removed = content.substring(index, index + length);
        content.delete(index, index + length);
        return removed;
    }
}

class InsertTextCommand implements EditorCommand {
    private final TextEditor editor;
    private final String text;
    private final Integer index;
    private int executedIndex;

    InsertTextCommand(TextEditor editor, String text) {
        this(editor, text, null);
    }

    InsertTextCommand(TextEditor editor, String text, Integer index) {
        this.editor = editor;
        this.text = text;
        this.index = index;
    }

    @Override
    public void execute() {
        executedIndex = index == null ? editor.getContent().length() : index;
        editor.insert(executedIndex, text);
    }

    @Override
    public void undo() {
        editor.delete(executedIndex, text.length());
    }
}

class DeleteTextCommand implements EditorCommand {
    private final TextEditor editor;
    private final int index;
    private final int length;
    private String deletedText = "";

    DeleteTextCommand(TextEditor editor, int index, int length) {
        this.editor = editor;
        this.index = index;
        this.length = length;
    }

    @Override
    public void execute() {
        deletedText = editor.delete(index, length);
    }

    @Override
    public void undo() {
        editor.insert(index, deletedText);
    }
}

class CommandHistory {
    private final Deque<EditorCommand> undoStack = new ArrayDeque<>();
    private final Deque<EditorCommand> redoStack = new ArrayDeque<>();

    public void execute(EditorCommand command) {
        command.execute();
        undoStack.push(command);
        redoStack.clear();
    }

    public void undo() {
        if (undoStack.isEmpty()) {
            return;
        }
        EditorCommand command = undoStack.pop();
        command.undo();
        redoStack.push(command);
    }

    public void redo() {
        if (redoStack.isEmpty()) {
            return;
        }
        EditorCommand command = redoStack.pop();
        command.execute();
        undoStack.push(command);
    }
}

public class TextEditorDemo {
    public static void main(String[] args) {
        TextEditor editor = new TextEditor();
        CommandHistory history = new CommandHistory();

        history.execute(new InsertTextCommand(editor, "hello"));
        history.execute(new InsertTextCommand(editor, " world"));
        System.out.println(editor.getContent());

        history.execute(new DeleteTextCommand(editor, 5, 6));
        System.out.println(editor.getContent());

        history.undo();
        System.out.println(editor.getContent());
    }
}
