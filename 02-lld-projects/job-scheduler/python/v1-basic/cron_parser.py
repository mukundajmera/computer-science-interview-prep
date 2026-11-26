from datetime import datetime, timedelta
from typing import Set

class CronParser:
    """
    Very basic cron parser for 5-part expressions (minute, hour, day of month, month, day of week).
    Handles *, integers, and simple comma-separated values.
    """
    @staticmethod
    def _parse_part(part: str, min_val: int, max_val: int) -> Set[int]:
        if part == "*":
            return set(range(min_val, max_val + 1))
        
        values = set()
        for p in part.split(","):
            if "-" in p:
                start, end = map(int, p.split("-"))
                values.update(range(start, end + 1))
            elif "/" in p:
                # Basic support for */X
                base, step = p.split("/")
                if base == "*":
                    values.update(range(min_val, max_val + 1, int(step)))
            else:
                values.add(int(p))
        return values

    @staticmethod
    def get_next_execution_time(cron_expr: str, after_timestamp: float) -> float:
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression, expected 5 parts")
            
        minutes = CronParser._parse_part(parts[0], 0, 59)
        hours = CronParser._parse_part(parts[1], 0, 23)
        days = CronParser._parse_part(parts[2], 1, 31)
        months = CronParser._parse_part(parts[3], 1, 12)
        days_of_week = CronParser._parse_part(parts[4], 0, 6) # 0 = Sunday

        current_time = datetime.fromtimestamp(after_timestamp)
        # Start searching from the next minute
        current_time = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Limit search to 5 years to prevent infinite loop on impossible dates (e.g. Feb 30)
        end_time = current_time + timedelta(days=365 * 5)

        while current_time < end_time:
            if (current_time.month in months and
                current_time.day in days and
                current_time.hour in hours and
                current_time.minute in minutes and
                (current_time.isoweekday() % 7) in days_of_week):
                return current_time.timestamp()
            
            current_time += timedelta(minutes=1)
            
        raise ValueError("Could not find next execution time for cron expression")
