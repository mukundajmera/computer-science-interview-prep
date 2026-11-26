from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional

from access_token import AccessToken
from compartment import Compartment
from package_size import PackageSize


class Locker:
    def __init__(
        self,
        small_count: int,
        medium_count: int,
        large_count: int,
        clock: Optional[Callable[[], datetime]] = None,
        token_ttl: timedelta = timedelta(days=7),
    ):
        self._compartments: List[Compartment] = []
        self._tokens: Dict[str, AccessToken] = {}
        self._token_counter = 0
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_ttl = token_ttl
        self._init_compartments(small_count, medium_count, large_count)

    def deposit_package(self, size: PackageSize) -> Optional[str]:
        compartment = self._find_exact_available(size)
        if compartment is None:
            return None

        compartment.mark_occupied()
        self._token_counter += 1
        token_code = f"T-{self._token_counter}"
        self._tokens[token_code] = AccessToken(
            code=token_code,
            compartment_id=compartment.compartment_id,
            expires_at=self._clock() + self._token_ttl,
        )
        return token_code

    def pickup(self, token_code: str) -> bool:
        token = self._tokens.get(token_code)
        if token is None or token.is_expired(self._clock()):
            return False

        compartment = self._find_by_id(token.compartment_id)
        if compartment is None:
            return False

        compartment.mark_available()
        self._tokens.pop(token_code, None)
        return True

    def clear_expired_deposits(self) -> int:
        now = self._clock()
        expired_codes = [code for code, token in self._tokens.items() if token.is_expired(now)]
        for code in expired_codes:
            token = self._tokens.pop(code)
            compartment = self._find_by_id(token.compartment_id)
            if compartment is not None:
                compartment.mark_available()
        return len(expired_codes)

    def get_active_token_count(self) -> int:
        return len(self._tokens)

    def _find_exact_available(self, size: PackageSize) -> Optional[Compartment]:
        for compartment in self._compartments:
            if compartment.size == size and compartment.is_available():
                return compartment
        return None

    def _find_by_id(self, compartment_id: str) -> Optional[Compartment]:
        for compartment in self._compartments:
            if compartment.compartment_id == compartment_id:
                return compartment
        return None

    def _init_compartments(self, small_count: int, medium_count: int, large_count: int) -> None:
        for idx in range(1, small_count + 1):
            self._compartments.append(Compartment(f"S-{idx}", PackageSize.SMALL))
        for idx in range(1, medium_count + 1):
            self._compartments.append(Compartment(f"M-{idx}", PackageSize.MEDIUM))
        for idx in range(1, large_count + 1):
            self._compartments.append(Compartment(f"L-{idx}", PackageSize.LARGE))
