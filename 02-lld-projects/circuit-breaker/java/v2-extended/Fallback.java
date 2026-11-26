public interface Fallback<T> {
    T apply(Exception e);
}
