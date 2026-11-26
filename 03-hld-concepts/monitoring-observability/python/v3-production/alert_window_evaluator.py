class AlertWindowEvaluator:
    def should_fire(self, value: float, threshold: float) -> bool:
        return value > threshold
