from sliding_window_aggregator import SlidingWindowAggregator, sum_aggregation
from dataclasses import dataclass

@dataclass
class Event:
    id: str
    timestamp: int
    value: float

def main():
    print("--- Stream Processing Demo ---")

    create_acc, add_fn, get_res = sum_aggregation()

    aggregator = SlidingWindowAggregator(
        window_size=5,
        slide_size=5,
        allowed_lateness=2,
        timestamp_extractor=lambda e: e.timestamp,
        create_accumulator=create_acc,
        add_fn=add_fn,
        get_result_fn=get_res
    )

    stream = [
        Event("1", 1, 10),
        Event("2", 3, 20),
        Event("3", 2, 5),   # Slightly out of order
        Event("4", 8, 15),
        Event("5", 4, 30),  # Late but within allowed lateness for window 0-5
        Event("6", 1, 50),  # Too late for window 0-5, should be discarded
        Event("7", 12, 5)
    ]

    for e in stream:
        print(f"Processing Event(t={e.timestamp}, v={e.value})")
        aggregator.process_event(e)

        results = aggregator.advance_watermark(e.timestamp - 1)
        for res in results:
            print(f"  Triggered: {res}")

    print("Advancing watermark to infinity...")
    results = aggregator.advance_watermark(2147483647) # Max int simulation
    for res in results:
        print(f"  Triggered: {res}")

if __name__ == "__main__":
    main()
