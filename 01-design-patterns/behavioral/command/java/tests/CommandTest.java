/**
 * Command Pattern - Unit Tests
 */

import java.util.*;

public class CommandTest {

    public static void main(String[] args) {
        CommandTest test = new CommandTest();
        test.textEditorCommandsSupportUndoAndRedo();
        test.macroCommandRollsBackCompletedStepsOnFailure();
        System.out.println("All tests passed.");
    }

    private void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }

    private void textEditorCommandsSupportUndoAndRedo() {
        TextEditor editor = new TextEditor();
        CommandHistory history = new CommandHistory();

        history.execute(new InsertTextCommand(editor, "hello"));
        history.execute(new InsertTextCommand(editor, " world"));
        history.execute(new DeleteTextCommand(editor, 5, 6));

        assertEquals("hello", editor.getContent());
        history.undo();
        assertEquals("hello world", editor.getContent());
        history.undo();
        assertEquals("hello", editor.getContent());
        history.redo();
        assertEquals("hello world", editor.getContent());
    }

    private void macroCommandRollsBackCompletedStepsOnFailure() {
        TextDocument document = new TextDocument();
        MacroCommand macro = new MacroCommand(
            "unsafe publish",
            Arrays.asList(
                new AppendLineCommand(document, "draft"),
                new FailingCommand("storage unavailable")
            )
        );

        try {
            macro.execute();
            throw new AssertionError("Expected IllegalStateException");
        } catch (IllegalStateException e) {
            // Expected
        }
        assertEquals("", document.getContent());
    }
}
