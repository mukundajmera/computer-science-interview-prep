package models;

import java.time.LocalDate;

public class MaintenanceWindow {
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final String reason;

    public MaintenanceWindow(LocalDate startDate, LocalDate endDate, String reason) {
        this.startDate = startDate;
        this.endDate = endDate;
        this.reason = reason;
    }

    public LocalDate getStartDate() { return startDate; }
    public LocalDate getEndDate() { return endDate; }
    public String getReason() { return reason; }

    public boolean overlaps(LocalDate start, LocalDate end) {
        return !start.isAfter(this.endDate) && !end.isBefore(this.startDate);
    }
}
