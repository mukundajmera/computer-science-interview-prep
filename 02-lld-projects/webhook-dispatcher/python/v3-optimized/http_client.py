from typing import Dict

class DeliveryResult:
    def __init__(self, status_code: int, success: bool):
        self.status_code = status_code
        self.success = success

class HttpClient:
    """Mockable HTTP Client interface."""
    def post(self, url: str, data: str, headers: Dict[str, str]) -> DeliveryResult:
        raise NotImplementedError()
