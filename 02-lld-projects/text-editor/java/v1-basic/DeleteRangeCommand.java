import java.util.List;

public class DeleteRangeCommand implements EditorCommand {
    private final TextBuffer buffer;
    private final int startLine;
    private final int endLine;
    private List<String> deletedLines;

    public DeleteRangeCommand(TextBuffer buffer, int startLine, int endLine) {
        this.buffer = buffer;
        this.startLine = startLine;
        this.endLine = endLine;
    }

    @Override
    public void execute() {
        this.deletedLines = buffer.deleteRange(startLine, endLine);
    }

    @Override
    public void undo() {
        if (deletedLines != null) {
            for (int i = 0; i < deletedLines.size(); i++) {
                buffer.insert(startLine + i, deletedLines.get(i));
            }
        }
    }
}
