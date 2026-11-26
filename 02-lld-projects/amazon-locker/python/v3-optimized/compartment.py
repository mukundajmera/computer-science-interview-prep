from dataclasses import dataclass

from compartment_status import CompartmentStatus
from package_size import PackageSize


@dataclass
class Compartment:
    compartment_id: str
    size: PackageSize
    status: CompartmentStatus = CompartmentStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == CompartmentStatus.AVAILABLE

    def mark_occupied(self) -> None:
        self.status = CompartmentStatus.OCCUPIED

    def mark_available(self) -> None:
        self.status = CompartmentStatus.AVAILABLE

    def mark_out_of_service(self) -> None:
        self.status = CompartmentStatus.OUT_OF_SERVICE
