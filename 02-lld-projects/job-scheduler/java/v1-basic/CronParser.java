package v1_basic;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.HashSet;
import java.util.Set;

public class CronParser {

    private static Set<Integer> parsePart(String part, int min, int max) {
        Set<Integer> values = new HashSet<>();
        if (part.equals("*")) {
            for (int i = min; i <= max; i++) values.add(i);
            return values;
        }
        for (String p : part.split(",")) {
            if (p.contains("-")) {
                String[] range = p.split("-");
                int start = Integer.parseInt(range[0]);
                int end = Integer.parseInt(range[1]);
                for (int i = start; i <= end; i++) values.add(i);
            } else if (p.contains("/")) {
                String[] stepStr = p.split("/");
                if (stepStr[0].equals("*")) {
                    int step = Integer.parseInt(stepStr[1]);
                    for (int i = min; i <= max; i += step) values.add(i);
                }
            } else {
                values.add(Integer.parseInt(p));
            }
        }
        return values;
    }

    public static long getNextExecutionTime(String cronExpr, long afterTimestampMillis) {
        String[] parts = cronExpr.split("\\s+");
        if (parts.length != 5) throw new IllegalArgumentException("Invalid cron expression");

        Set<Integer> minutes = parsePart(parts[0], 0, 59);
        Set<Integer> hours = parsePart(parts[1], 0, 23);
        Set<Integer> days = parsePart(parts[2], 1, 31);
        Set<Integer> months = parsePart(parts[3], 1, 12);
        Set<Integer> daysOfWeek = parsePart(parts[4], 0, 6);

        LocalDateTime current = LocalDateTime.ofEpochSecond(afterTimestampMillis / 1000, 0, ZoneId.systemDefault().getRules().getOffset(java.time.Instant.now()));
        current = current.truncatedTo(ChronoUnit.MINUTES).plusMinutes(1);
        
        LocalDateTime end = current.plusYears(5);

        while (current.isBefore(end)) {
            int dow = current.getDayOfWeek().getValue() % 7; // Sunday is 0 here based on modulo, if DayOfWeek is 7 (Sun) % 7 = 0
            if (months.contains(current.getMonthValue()) &&
                days.contains(current.getDayOfMonth()) &&
                hours.contains(current.getHour()) &&
                minutes.contains(current.getMinute()) &&
                daysOfWeek.contains(dow)) {
                return current.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
            }
            current = current.plusMinutes(1);
        }

        throw new IllegalArgumentException("Could not find next execution time");
    }
}
