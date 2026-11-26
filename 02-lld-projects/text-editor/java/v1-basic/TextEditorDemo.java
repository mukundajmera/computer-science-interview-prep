public class TextEditorDemo {
    public static void main(String[] args) {
        TextEditor editor = new TextEditor();
        
        System.out.println("Inserting lines...");
        editor.insert(1, "Hello");
        editor.insert(2, "World");
        editor.insert(3, "!");
        editor.display();
        
        System.out.println("\nUndoing...");
        editor.undo();
        editor.display();
        
        System.out.println("\nRedoing...");
        editor.redo();
        editor.display();
        
        System.out.println("\nCopying and pasting...");
        editor.copy(1, 2);
        editor.paste(4);
        editor.display();
        
        System.out.println("\nDeleting a range...");
        editor.deleteRange(2, 4);
        editor.display();
    }
}
