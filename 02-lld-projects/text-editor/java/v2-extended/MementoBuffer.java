

import java.util.List;

public class MementoBuffer implements TextBuffer {
    private LineBuffer buffer;

    public MementoBuffer() {
        this.buffer = new LineBuffer();
    }

    @Override
    public void insert(int lineNum, String text) {
        buffer.insert(lineNum, text);
    }

    @Override
    public void delete(int lineNum) {
        buffer.delete(lineNum);
    }

    @Override
    public void replace(int lineNum, String text) {
        buffer.replace(lineNum, text);
    }

    @Override
    public List<String> getAll() {
        return buffer.getAll();
    }

    public EditorMemento save() {
        return new EditorMemento(getAll());
    }

    public void restore(EditorMemento memento) {
        this.buffer = new LineBuffer();
        List<String> state = memento.getState();
        for (int i = 0; i < state.size(); i++) {
            this.buffer.insert(i + 1, state.get(i));
        }
    }
}
