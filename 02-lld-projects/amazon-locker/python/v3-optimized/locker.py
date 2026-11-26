from datetime import timedelta
from typing import Dict, List, Optional

from access_token import AccessToken
from allocation_policy import AllocationPolicy
from clock import Clock, SystemClock
from compartment import Compartment
from compartment_status import CompartmentStatus
from fallback_size_policy import FallbackSizePolicy
from package_size import PackageSize
from reservation import Reservation
from reservation_status import ReservationStatus


class Locker:
    def __init__(
        self,
        small_count: int,
        medium_count: int,
        large_count: int,
        clock: Optional[Clock] = None,
        token_ttl: timedelta = timedelta(days=7),
        reservation_ttl: timedelta = timedelta(minutes=3),
        allocation_policy: Optional[AllocationPolicy] = None,
    ):
        self._compartments: List[Compartment] = []
        self._tokens: Dict[str, AccessToken] = {}
        self._reservations: Dict[str, Reservation] = {}
        self._clock = clock or SystemClock()
        self._token_ttl = token_ttl
        self._reservation_ttl = reservation_ttl
        self._allocation_policy = allocation_policy or FallbackSizePolicy()
        self._token_counter = 0
        self._reservation_counter = 0
        self._init_compartments(small_count, medium_count, large_count)

    def deposit_package(self, size: PackageSize) -> Optional[str]:
        reservation_id = self.reserve_compartment(size)
        if reservation_id is None:
            return None
        return self.confirm_deposit(reservation_id)

    def reserve_compartment(self, size: PackageSize) -> Optional[str]:
        self.expire_reservations()
        compartment = self._allocation_policy.select(self._compartments, size)
        if compartment is None:
            return None

        compartment.mark_occupied()
        self._reservation_counter += 1
        reservation_id = f"R-{self._reservation_counter}"
        self._reservations[reservation_id] = Reservation(
            reservation_id=reservation_id,
            compartment_id=compartment.compartment_id,
            expires_at=self._clock.now() + self._reservation_ttl,
        )
        return reservation_id

    def confirm_deposit(self, reservation_id: str) -> Optional[str]:
        reservation = self._reservations.get(reservation_id)
        if reservation is None or reservation.status != ReservationStatus.RESERVED:
            return None
        if reservation.is_expired(self._clock.now()):
            reservation.status = ReservationStatus.EXPIRED
            self._release_compartment(reservation.compartment_id)
            self._reservations.pop(reservation_id, None)
            return None

        reservation.status = ReservationStatus.CONFIRMED
        self._token_counter += 1
        token_code = f"T-{self._token_counter}"
        self._tokens[token_code] = AccessToken(
            code=token_code,
            compartment_id=reservation.compartment_id,
            expires_at=self._clock.now() + self._token_ttl,
        )
        self._reservations.pop(reservation_id, None)
        return token_code

    def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = self._reservations.get(reservation_id)
        if reservation is None or reservation.status != ReservationStatus.RESERVED:
            return False

        reservation.status = ReservationStatus.CANCELLED
        self._release_compartment(reservation.compartment_id)
        self._reservations.pop(reservation_id, None)
        return True

    def expire_reservations(self) -> int:
        now = self._clock.now()
        expired_ids = [rid for rid, reservation in self._reservations.items() if reservation.is_expired(now)]
        for reservation_id in expired_ids:
            reservation = self._reservations.pop(reservation_id)
            reservation.status = ReservationStatus.EXPIRED
            self._release_compartment(reservation.compartment_id)
        return len(expired_ids)

    def pickup(self, token_code: str) -> bool:
        token = self._tokens.get(token_code)
        if token is None or token.is_expired(self._clock.now()):
            return False

        self._release_compartment(token.compartment_id)
        self._tokens.pop(token_code, None)
        return True

    def clear_expired_deposits(self) -> int:
        now = self._clock.now()
        expired_codes = [code for code, token in self._tokens.items() if token.is_expired(now)]
        for token_code in expired_codes:
            token = self._tokens.pop(token_code)
            self._release_compartment(token.compartment_id)
        return len(expired_codes)

    def get_compartment_status(self, compartment_id: str) -> Optional[CompartmentStatus]:
        compartment = self._find_compartment(compartment_id)
        return None if compartment is None else compartment.status

    def _release_compartment(self, compartment_id: str) -> None:
        compartment = self._find_compartment(compartment_id)
        if compartment is not None:
            compartment.mark_available()

    def _find_compartment(self, compartment_id: str) -> Optional[Compartment]:
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
