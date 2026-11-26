import java.util.List;

public interface AllocationPolicy {
    Compartment select(List<Compartment> compartments, PackageSize requestedSize);
}
