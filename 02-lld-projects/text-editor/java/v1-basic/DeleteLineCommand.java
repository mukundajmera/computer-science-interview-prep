public class DeleteLineCommand implements EditorCommand {
    private final TextBuffer buffer;
    private final int lineNum;
    private String deletedText;

    public DeleteLineCommand(TextBuffer buffer, int lineNum) {
        this.buffer = buffer;
        this.lineNum = lineNum;
    }

    @Override
    public void execute() {
        this.deletedText = buffer.delete(lineNum);
    }

    @Override
    public void undo() {
        if (this.deletedText != null) {
            buffer.insert(lineNum, deletedText);
        }
    }
}
