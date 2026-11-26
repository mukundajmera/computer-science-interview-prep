"""Interview-scale gateway with routing + simple per-route throttling."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class RouteConfig:
    backend_url: str
    auth_required: bool
    max_requests: int
    used_requests: int = 0


class SimpleGateway:
    def __init__(self) -> None:
        self._routes: Dict[str, RouteConfig] = {}

    def add_route(
        self,
        prefix: str,
        backend_url: str,
        auth_required: bool,
        max_requests: int,
    ) -> None:
        self._routes[prefix] = RouteConfig(
            backend_url=backend_url,
            auth_required=auth_required,
            max_requests=max_requests,
        )

    def handle(self, path: str, is_authenticated: bool) -> str:
        for prefix, config in self._routes.items():
            if not path.startswith(prefix):
                continue
            if config.auth_required and not is_authenticated:
                return "401 Unauthorized"
            if config.used_requests >= config.max_requests:
                return "429 Too Many Requests"
            config.used_requests += 1
            return f"200 Forward -> {config.backend_url}"
        return "404 Not Found"


if __name__ == "__main__":
    gateway = SimpleGateway()
    gateway.add_route("/users", "http://user-service:8080", auth_required=True, max_requests=2)
    print(gateway.handle("/users/1", is_authenticated=False))
    print(gateway.handle("/users/1", is_authenticated=True))
    print(gateway.handle("/users/2", is_authenticated=True))
    print(gateway.handle("/users/3", is_authenticated=True))
