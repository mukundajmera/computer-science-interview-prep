from typing import Iterable, Optional

from compartment import Compartment
from package_size import PackageSize


class ExactSizePolicy:
    def select(self, compartments: Iterable[Compartment], requested_size: PackageSize) -> Optional[Compartment]:
        for compartment in compartments:
            if compartment.size == requested_size and compartment.is_available():
                return compartment
        return None
