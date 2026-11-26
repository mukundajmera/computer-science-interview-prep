/**
 * Memento Pattern - Text Editor Undo
 */

import java.util.*;

// Memento - stores state
class EditorMemento {
    private final String content;
    private final int cursorPosition;
    
    public EditorMemento(String content, int cursorPosition) {
        this.content = content;
        this.cursorPosition = cursorPosition;
    }
    
    public String getContent() { return content; }
    public int getCursorPosition() { return cursorPosition; }
}

// Originator - creates and restores from mementos
class TextEditor {
    private String content = "";
    private int cursorPosition = 0;
    
    public void type(String text) {
        content = content.substring(0, cursorPosition) + 
                  text + 
                  content.substring(cursorPosition);
        cursorPosition += text.length();
    }
    
    public void delete() {
        if (cursorPosition > 0) {
            content = content.substring(0, cursorPosition - 1) + 
                      content.substring(cursorPosition);
            cursorPosition--;
        }
    }
    
    public EditorMemento save() {
        return new EditorMemento(content, cursorPosition);
    }
    
    public void restore(EditorMemento memento) {
        content = memento.getContent();
        cursorPosition = memento.getCursorPosition();
    }
    
    public String getContent() { return content; }
    
    @Override
    public String toString() {
        return "Content: \"" + content + "\" (cursor at " + cursorPosition + ")";
    }
}

// Caretaker - manages mementos
class History {
    private Stack<EditorMemento> undoStack = new Stack<>();
    private Stack<EditorMemento> redoStack = new Stack<>();
    
    public void push(EditorMemento memento) {
        undoStack.push(memento);
        redoStack.clear();
    }
    
    public EditorMemento undo() {
        if (undoStack.size() > 1) {
            redoStack.push(undoStack.pop());
            return undoStack.peek();
        }
        return undoStack.isEmpty() ? null : undoStack.peek();
    }
    
    public EditorMemento redo() {
        if (!redoStack.isEmpty()) {
            EditorMemento memento = redoStack.pop();
            undoStack.push(memento);
            return memento;
        }
        return null;
    }
}

public class MementoDemo {
    public static void main(String[] args) {
        TextEditor editor = new TextEditor();
        History history = new History();
        
        // Save initial state
        history.push(editor.save());
        
        // Make changes
        editor.type("Hello");
        System.out.println("After 'Hello': " + editor);
        history.push(editor.save());
        
        editor.type(" World");
        System.out.println("After ' World': " + editor);
        history.push(editor.save());
        
        editor.type("!");
        System.out.println("After '!': " + editor);
        history.push(editor.save());
        
        // Undo
        System.out.println("\n=== Undo ===");
        editor.restore(history.undo());
        System.out.println("Undo: " + editor);
        
        editor.restore(history.undo());
        System.out.println("Undo: " + editor);
        
        // Redo
        System.out.println("\n=== Redo ===");
        editor.restore(history.redo());
        System.out.println("Redo: " + editor);
    }
}
