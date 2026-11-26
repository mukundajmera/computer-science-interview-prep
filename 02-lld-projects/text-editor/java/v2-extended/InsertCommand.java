

public class InsertCommand implements Command {
    private final MementoBuffer buffer;
    private final int lineNum;
    private final String text;
    private EditorMemento memento;

    public InsertCommand(MementoBuffer buffer, int lineNum, String text) {
        this.buffer = buffer;
        this.lineNum = lineNum;
        this.text = text;
    }

    @Override
    public void execute() {
        this.memento = buffer.save();
        buffer.insert(lineNum, text);
    }

    @Override
    public void undo() {
        if (this.memento != null) {
            buffer.restore(this.memento);
        }
    }
}
