public class InsertLineCommand implements EditorCommand {
    private final TextBuffer buffer;
    private final int lineNum;
    private final String text;

    public InsertLineCommand(TextBuffer buffer, int lineNum, String text) {
        this.buffer = buffer;
        this.lineNum = lineNum;
        this.text = text;
    }

    @Override
    public void execute() {
        buffer.insert(lineNum, text);
    }

    @Override
    public void undo() {
        buffer.delete(lineNum);
    }
}
