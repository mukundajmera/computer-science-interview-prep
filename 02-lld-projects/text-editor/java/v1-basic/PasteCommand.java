import java.util.List;

public class PasteCommand implements EditorCommand {
    private final TextBuffer buffer;
    private final int lineNum;
    private final List<String> content;

    public PasteCommand(TextBuffer buffer, int lineNum, List<String> content) {
        this.buffer = buffer;
        this.lineNum = lineNum;
        this.content = content;
    }

    @Override
    public void execute() {
        if (content != null) {
            for (int i = 0; i < content.size(); i++) {
                buffer.insert(lineNum + i, content.get(i));
            }
        }
    }

    @Override
    public void undo() {
        if (content != null && !content.isEmpty()) {
            buffer.deleteRange(lineNum, lineNum + content.size() - 1);
        }
    }
}
