

public class ReplaceCommand implements Command {
    private final MementoBuffer buffer;
    private final int lineNum;
    private final String newText;
    private EditorMemento memento;

    public ReplaceCommand(MementoBuffer buffer, int lineNum, String newText) {
        this.buffer = buffer;
        this.lineNum = lineNum;
        this.newText = newText;
    }

    @Override
    public void execute() {
        this.memento = buffer.save();
        buffer.replace(lineNum, newText);
    }

    @Override
    public void undo() {
        if (this.memento != null) {
            buffer.restore(this.memento);
        }
    }
}
