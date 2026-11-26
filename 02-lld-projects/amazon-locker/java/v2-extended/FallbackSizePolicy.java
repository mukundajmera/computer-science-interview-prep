import java.util.List;

public class FallbackSizePolicy implements AllocationPolicy {
    @Override
    public Compartment select(List<Compartment> compartments, PackageSize requestedSize) {
        PackageSize[] order = new PackageSize[]{PackageSize.SMALL, PackageSize.MEDIUM, PackageSize.LARGE};
        int start = 0;
        for (int i = 0; i < order.length; i++) {
            if (order[i] == requestedSize) {
                start = i;
                break;
            }
        }

        for (int i = start; i < order.length; i++) {
            for (Compartment c : compartments) {
                if (c.getSize() == order[i] && c.isAvailable()) {
                    return c;
                }
            }
        }
        return null;
    }
}
