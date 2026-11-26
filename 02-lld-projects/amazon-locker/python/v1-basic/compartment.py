from dataclasses import dataclass

from package_size import PackageSize


@dataclass
class Compartment:
    compartment_id: str
    size: PackageSize
    occupied: bool = False

    def is_available(self) -> bool:
        return not self.occupied

    def mark_occupied(self) -> None:
        self.occupied = True

    def mark_available(self) -> None:
        self.occupied = False
