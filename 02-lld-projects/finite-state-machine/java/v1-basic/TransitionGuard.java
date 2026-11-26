public interface TransitionGuard<C> {
    boolean evaluate(C context);
}
