

public class DeleteCommand implements Command {
    private final MementoBuffer buffer;
    private final int lineNum;
    private EditorMemento memento;

    public DeleteCommand(MementoBuffer buffer, int lineNum) {
        this.buffer = buffer;
        this.lineNum = lineNum;
    }

    @Override
    public void execute() {
        this.memento = buffer.save();
        buffer.delete(lineNum);
    }

    @Override
    public void undo() {
        if (this.memento != null) {
            buffer.restore(this.memento);
        }
    }
}
