from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional

from access_token import AccessToken
from allocation_policy import AllocationPolicy
from compartment import Compartment
from compartment_status import CompartmentStatus
from exact_size_policy import ExactSizePolicy
from package_size import PackageSize


class Locker:
    def __init__(
        self,
        small_count: int,
        medium_count: int,
        large_count: int,
        clock: Optional[Callable[[], datetime]] = None,
        token_ttl: timedelta = timedelta(days=7),
        allocation_policy: Optional[AllocationPolicy] = None,
    ):
        self._compartments: List[Compartment] = []
        self._tokens: Dict[str, AccessToken] = {}
        self._token_counter = 0
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_ttl = token_ttl
        self._allocation_policy = allocation_policy or ExactSizePolicy()
        self._init_compartments(small_count, medium_count, large_count)

    def set_allocation_policy(self, allocation_policy: AllocationPolicy) -> None:
        self._allocation_policy = allocation_policy

    def deposit_package(self, size: PackageSize) -> Optional[str]:
        compartment = self._allocation_policy.select(self._compartments, size)
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

    def mark_compartment_out_of_service(self, compartment_id: str) -> bool:
        compartment = self._find_by_id(compartment_id)
        if compartment is None or compartment.status == CompartmentStatus.OCCUPIED:
            return False
        compartment.mark_out_of_service()
        return True

    def get_compartment_status(self, compartment_id: str) -> Optional[CompartmentStatus]:
        compartment = self._find_by_id(compartment_id)
        return None if compartment is None else compartment.status

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
