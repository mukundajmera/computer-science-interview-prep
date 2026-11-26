public interface StateAction<C> {
    void execute(C context);
}
