from typing import Iterable, Optional

from compartment import Compartment
from package_size import PackageSize


class FallbackSizePolicy:
    ORDER = [PackageSize.SMALL, PackageSize.MEDIUM, PackageSize.LARGE]

    def select(self, compartments: Iterable[Compartment], requested_size: PackageSize) -> Optional[Compartment]:
        try:
            start_index = self.ORDER.index(requested_size)
        except ValueError:
            return None

        for target_size in self.ORDER[start_index:]:
            for compartment in compartments:
                if compartment.size == target_size and compartment.is_available():
                    return compartment
        return None
