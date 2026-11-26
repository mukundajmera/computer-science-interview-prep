import java.util.*;

public class BatchAuctionMatcher {
    public static Map<Trip, Driver> match(List<Driver> drivers, List<Trip> trips) {
        Map<Trip, Driver> matches = new HashMap<>();
        
        if (drivers.isEmpty() || trips.isEmpty()) {
            return matches;
        }

        double[][] costMatrix = new double[trips.size()][drivers.size()];
        
        for (int i = 0; i < trips.size(); i++) {
            for (int j = 0; j < drivers.size(); j++) {
                costMatrix[i][j] = trips.get(i).getOrigin().distanceTo(drivers.get(j).getLocation());
            }
        }

        HungarianAlgorithm hungarian = new HungarianAlgorithm(costMatrix);
        int[] result = hungarian.execute();
        
        for (int i = 0; i < result.length; i++) {
            if (result[i] != -1 && i < trips.size()) {
                matches.put(trips.get(i), drivers.get(result[i]));
            }
        }

        return matches;
    }
}
