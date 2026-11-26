package v2_extended;
import java.util.ArrayList;
import java.util.List;

public class WindowStrategy {
    private final long windowSizeMs;
    private final long slideStepMs;

    public WindowStrategy(long windowSizeMs, long slideStepMs) {
        this.windowSizeMs = windowSizeMs;
        this.slideStepMs = slideStepMs;
    }

    public List<Long> getOverlappingWindows(long timestamp) {
        List<Long> windows = new ArrayList<>();
        long firstWindowStart = ((timestamp - windowSizeMs + slideStepMs) / slideStepMs) * slideStepMs;
        
        long currentStart = firstWindowStart;
        while (currentStart <= timestamp) {
            windows.add(currentStart);
            currentStart += slideStepMs;
        }
        return windows;
    }
}
