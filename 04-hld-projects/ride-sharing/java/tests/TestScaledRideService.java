import java.util.List;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.*;

public class TestScaledRideService {

    private Object createIndexer(double res) throws Exception {
        Class<?> clazz = Class.forName("ridesharing.v2.H3SpatialIndexer");
        Constructor<?> ctor = clazz.getDeclaredConstructor(double.class);
        ctor.setAccessible(true);
        return ctor.newInstance(res);
    }

    private Object createIndexer() throws Exception {
        Class<?> clazz = Class.forName("ridesharing.v2.H3SpatialIndexer");
        Constructor<?> ctor = clazz.getDeclaredConstructor();
        ctor.setAccessible(true);
        return ctor.newInstance();
    }
    
    private Object createHexCell(int q, int r) throws Exception {
        Class<?> clazz = Class.forName("ridesharing.v2.HexCell");
        Constructor<?> ctor = clazz.getDeclaredConstructor(int.class, int.class);
        ctor.setAccessible(true);
        return ctor.newInstance(q, r);
    }

    @Test
    public void testLatLngToCell() throws Exception {
        Object indexer = createIndexer(0.01);
        
        Method m = indexer.getClass().getDeclaredMethod("latLngToCell", double.class, double.class);
        m.setAccessible(true);
        
        Object cell1 = m.invoke(indexer, 0.0, 0.0);
        Field qField = cell1.getClass().getDeclaredField("q");
        Field rField = cell1.getClass().getDeclaredField("r");
        qField.setAccessible(true);
        rField.setAccessible(true);
        assertEquals(0, qField.getInt(cell1));
        assertEquals(0, rField.getInt(cell1));
        
        Object cell2 = m.invoke(indexer, 0.001, 0.001);
        assertEquals(cell1, cell2);
        
        Object cell3 = m.invoke(indexer, 0.05, 0.05);
        assertNotEquals(cell1, cell3);
    }
    
    @Test
    public void testGetKRing() throws Exception {
        Object indexer = createIndexer();
        Object center = createHexCell(0, 0);
        
        Method getKRing = indexer.getClass().getDeclaredMethod("getKRing", center.getClass(), int.class);
        getKRing.setAccessible(true);
        
        List<?> k0 = (List<?>) getKRing.invoke(indexer, center, 0);
        assertEquals(1, k0.size());
        assertTrue(k0.contains(center));
        
        List<?> k1 = (List<?>) getKRing.invoke(indexer, center, 1);
        assertEquals(7, k1.size());
        
        List<?> k2 = (List<?>) getKRing.invoke(indexer, center, 2);
        assertEquals(19, k2.size());
    }
    
    @Test
    public void testUpdateAndFindDrivers() throws Exception {
        Object indexer = createIndexer();
        
        Method updateLocation = indexer.getClass().getDeclaredMethod("updateDriverLocation", String.class, double.class, double.class);
        updateLocation.setAccessible(true);
        
        updateLocation.invoke(indexer, "driver1", 0.0, 0.0);
        updateLocation.invoke(indexer, "driver2", 0.01, 0.01);
        updateLocation.invoke(indexer, "driver3", 0.1, 0.1);
        
        Method findDrivers = indexer.getClass().getDeclaredMethod("findDriversInKRing", double.class, double.class, int.class);
        findDrivers.setAccessible(true);
        
        List<String> driversK0 = (List<String>) findDrivers.invoke(indexer, 0.0, 0.0, 0);
        assertTrue(driversK0.contains("driver1"));
        assertFalse(driversK0.contains("driver3"));
        
        List<String> driversK1 = (List<String>) findDrivers.invoke(indexer, 0.0, 0.0, 2);
        assertTrue(driversK1.contains("driver1"));
        assertTrue(driversK1.contains("driver2"));
        assertFalse(driversK1.contains("driver3"));
        
        updateLocation.invoke(indexer, "driver1", 0.1, 0.1);
        List<String> driversK1After = (List<String>) findDrivers.invoke(indexer, 0.0, 0.0, 2);
        assertFalse(driversK1After.contains("driver1"));
        assertTrue(driversK1After.contains("driver2"));
    }
    
    @Test
    public void testAdditionalCoverage() throws Exception {
        Object indexer = createIndexer();
        Method latLngToCell = indexer.getClass().getDeclaredMethod("latLngToCell", double.class, double.class);
        latLngToCell.setAccessible(true);
        
        Object cell1 = latLngToCell.invoke(indexer, 0.0, 0.0);
        assertEquals(cell1.hashCode(), cell1.hashCode());
        assertEquals("0,0", cell1.toString());
        assertFalse(cell1.equals(null));
        assertFalse(cell1.equals("string"));
    }
}
