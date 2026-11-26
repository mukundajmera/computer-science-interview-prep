from typing import Iterable, Optional, Protocol

from compartment import Compartment
from package_size import PackageSize


class AllocationPolicy(Protocol):
    def select(self, compartments: Iterable[Compartment], requested_size: PackageSize) -> Optional[Compartment]:
        ...
