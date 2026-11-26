/** Simple CAP behavior simulator during partition events. */
public class CapSystem {
    public enum Mode { CP, AP }

    private final Mode mode;

    public CapSystem(Mode mode) {
        if (mode == null) {
            throw new IllegalArgumentException("mode must not be null");
        }
        this.mode = mode;
    }

    public String readDuringPartition() {
        return mode == Mode.CP ? "REJECTED_FOR_CONSISTENCY" : "STALE_OK";
    }
}
