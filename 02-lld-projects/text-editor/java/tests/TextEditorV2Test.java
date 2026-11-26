

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;

public class TextEditorV2Test {

    @Test
    public void testInsertAndDelete() {
        TextEditor editor = new TextEditor(100);
        editor.insert(1, "Hello");
        editor.insert(2, "World");
        assertEquals(Arrays.asList("Hello", "World"), editor.getAllLines());
        
        editor.delete(1);
        assertEquals(Arrays.asList("World"), editor.getAllLines());
    }

    @Test
    public void testUndoRedo() {
        TextEditor editor = new TextEditor(100);
        editor.insert(1, "Line 1");
        editor.insert(2, "Line 2");
        assertEquals(Arrays.asList("Line 1", "Line 2"), editor.getAllLines());
        
        editor.undo();
        assertEquals(Arrays.asList("Line 1"), editor.getAllLines());
        
        editor.redo();
        assertEquals(Arrays.asList("Line 1", "Line 2"), editor.getAllLines());
        
        editor.delete(1);
        assertEquals(Arrays.asList("Line 2"), editor.getAllLines());
        
        editor.undo();
        assertEquals(Arrays.asList("Line 1", "Line 2"), editor.getAllLines());
    }

    @Test
    public void testMacroRecording() {
        TextEditor editor = new TextEditor(100);
        editor.insert(1, "Initial");
        
        editor.startMacro();
        editor.insert(2, "Macro 1");
        editor.insert(3, "Macro 2");
        MacroCommand macro = editor.stopMacro();
        
        assertEquals(Arrays.asList("Initial", "Macro 1", "Macro 2"), editor.getAllLines());
        
        editor.undo(); // Undoes the entire macro
        assertEquals(Arrays.asList("Initial"), editor.getAllLines());
        
        editor.executeMacro(macro);
        assertEquals(Arrays.asList("Initial", "Macro 1", "Macro 2"), editor.getAllLines());
    }

    @Test
    public void testHistoryLimit() {
        TextEditor editor = new TextEditor(2); // Limit to 2 commands
        editor.insert(1, "Line 1");
        editor.insert(2, "Line 2");
        editor.insert(3, "Line 3");
        
        editor.undo(); // undo Line 3
        editor.undo(); // undo Line 2
        editor.undo(); // should do nothing, as limit is 2
        
        assertEquals(Arrays.asList("Line 1"), editor.getAllLines());
    }

    @Test
    public void testReplace() {
        TextEditor editor = new TextEditor(100);
        editor.insert(1, "Old Text");
        editor.replace(1, "New Text");
        assertEquals(Arrays.asList("New Text"), editor.getAllLines());
        
        editor.undo();
        assertEquals(Arrays.asList("Old Text"), editor.getAllLines());
    }
}
