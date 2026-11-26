class Bucket:
    def __init__(self, start_time: float):
        self.start_time = start_time
        self.success_count = 0
        self.failure_count = 0
        self.slow_call_count = 0
