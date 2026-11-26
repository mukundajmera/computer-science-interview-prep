

public interface TransitionGuard<C, P> {
    boolean evaluate(C context, P payload);
}
