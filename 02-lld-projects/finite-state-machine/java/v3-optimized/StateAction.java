

public interface StateAction<C, P> {
    void execute(C context, P payload);
}
