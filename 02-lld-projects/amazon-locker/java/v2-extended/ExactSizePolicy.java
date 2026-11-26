import java.util.List;

public class ExactSizePolicy implements AllocationPolicy {
    @Override
    public Compartment select(List<Compartment> compartments, PackageSize requestedSize) {
        for (Compartment c : compartments) {
            if (c.getSize() == requestedSize && c.isAvailable()) {
                return c;
            }
        }
        return null;
    }
}
