import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class TextEditorTest {

    private TextEditor editor;

    @BeforeEach
    public void setUp() {
        editor = new TextEditor();
    }

    @Test
    public void testInsertAndDisplay() {
        editor.insert(1, "First line");
        editor.insert(2, "Second line");
        
        List<String> lines = editor.getAllLines();
        assertEquals(2, lines.size());
        assertEquals("First line", lines.get(0));
        assertEquals("Second line", lines.get(1));
    }

    @Test
    public void testDeleteRange() {
        editor.insert(1, "L1");
        editor.insert(2, "L2");
        editor.insert(3, "L3");
        editor.insert(4, "L4");

        editor.deleteRange(2, 3);
        List<String> lines = editor.getAllLines();
        
        assertEquals(2, lines.size());
        assertEquals("L1", lines.get(0));
        assertEquals("L4", lines.get(1));
    }

    @Test
    public void testCopyPaste() {
        editor.insert(1, "A");
        editor.insert(2, "B");
        
        editor.copy(1, 2);
        editor.paste(3);
        
        List<String> lines = editor.getAllLines();
        assertEquals(4, lines.size());
        assertEquals("A", lines.get(0));
        assertEquals("B", lines.get(1));
        assertEquals("A", lines.get(2));
        assertEquals("B", lines.get(3));
    }

    @Test
    public void testUndoRedoInvalidation() {
        editor.insert(1, "One");
        editor.insert(2, "Two");
        
        // Undo "Two"
        editor.undo();
        assertEquals(1, editor.getAllLines().size());
        assertEquals("One", editor.getAllLines().get(0));
        
        // Redo "Two"
        editor.redo();
        assertEquals(2, editor.getAllLines().size());
        assertEquals("Two", editor.getAllLines().get(1));
        
        // Undo "Two" again
        editor.undo();
        
        // Insert new line (should invalidate redo stack)
        editor.insert(2, "Three");
        assertEquals(2, editor.getAllLines().size());
        assertEquals("Three", editor.getAllLines().get(1));
        
        // Redo should do nothing
        editor.redo();
        assertEquals(2, editor.getAllLines().size());
        assertEquals("Three", editor.getAllLines().get(1));
    }
}
