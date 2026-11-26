/**
 * Memento Pattern - v2/v3 smoke tests without external test dependencies.
 */

import java.util.Arrays;

class MementoTest {
    public static void main(String[] args) {
        testV2BoundedHistory();
        testV3Transactions();
    }

    private static void testV2BoundedHistory() {
        VersionedTextEditor editor = new VersionedTextEditor();
        BoundedEditorHistory history = new BoundedEditorHistory(3);

        history.push(editor.save("empty"));
        editor.type("Hello");
        history.push(editor.save("greeting"));
        editor.type(" World");
        history.push(editor.save("subject"));
        editor.delete();
        history.push(editor.save("trimmed"));

        assertEquals(
            Arrays.asList("greeting", "subject", "trimmed").toString(),
            history.labels().toString()
        );

        editor.restore(history.undo());
        assertEquals("Hello World", editor.getContent());
        editor.restore(history.undo());
        assertEquals("Hello", editor.getContent());
        editor.restore(history.undo());
        assertEquals("Hello", editor.getContent());

        editor.restore(history.redo());
        assertEquals("Hello World", editor.getContent());
    }

    private static void testV3Transactions() {
        TransactionalTextEditor editor = new TransactionalTextEditor();
        CheckpointHistory history = new CheckpointHistory(editor);

        history.snapshot("empty");
        editor.type("Draft");
        history.snapshot("draft");
        history.saveCheckpoint("approved-draft");

        history.beginTransaction("risky rewrite");
        editor.type(" unsafe");
        history.rollbackTransaction();
        assertEquals("Draft", editor.getContent());

        history.beginTransaction("publish edit");
        editor.type(" v2");
        history.commitTransaction("published");
        assertEquals("Draft v2", editor.getContent());

        history.undo();
        assertEquals("Draft", editor.getContent());
        history.redo();
        assertEquals("Draft v2", editor.getContent());

        history.restoreCheckpoint("approved-draft");
        assertEquals("Draft", editor.getContent());
    }

    private static void assertEquals(String expected, String actual) {
        if (!expected.equals(actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }
}
